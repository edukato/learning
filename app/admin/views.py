import datetime

from flask import flash, redirect, render_template, url_for, abort
from flask_login import login_required, current_user

from . import admin
from ..models import Client, Subject, TrainingChoice, Task, Schedule, Teacher, Material, Salary
from .. import db
from .forms import SubjectEditForm, SubjectAddForm, ChoiceAddForm, ChoiceEditForm, TaskAddForm, SalaryForm, AddMaterial
from ..utils import awesome_date


def check_admin():
    if not (current_user.status == 2):
        abort(403)


@admin.route('/admin')
@login_required
def dashboard():
    check_admin()
    return render_template('admin/dashboard.html', title='Главная страница')


@admin.route('/admin/clients')
@login_required
def clients():
    check_admin()
    students = Client.query.filter(Client.status == 1).all()
    teachers = Client.query.filter(Client.status == 3).all()
    return render_template('admin/clients.html', students=students, teachers=teachers, title='Клиенты')


@admin.route('/admin/subjects')
@login_required
def subjects():
    check_admin()
    list_subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=list_subjects, title='Клиенты')


@admin.route('/admin/subject/<int:id>', methods=['GET', 'POST'])
@login_required
def subject(id):
    check_admin()
    subject = Subject.query.get_or_404(id)

    choices = TrainingChoice.query.filter(TrainingChoice.subject_id == id).order_by(TrainingChoice.number.asc()).all()
    return render_template('admin/subject.html', choices=choices, subject=subject, title=subject.subject)


@admin.route('/admin/subject/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def subject_edit(id):
    check_admin()

    subject = Subject.query.get_or_404(id)
    form = SubjectEditForm(obj=subject)
    if form.validate_on_submit():
        subject.subject = form.subject.data
        subject.description = form.description.data
        flash('Изменения внесены')
        db.session.commit()
        return redirect(url_for('admin.subject', id=id))

    form.subject.data = subject.subject
    form.description.data = subject.description

    return render_template('admin/subject_edit.html', form=form, subject=subject, title=subject.subject)


@admin.route('/admin/subject/add', methods=['GET', 'POST'])
@login_required
def subject_add():
    check_admin()

    form = SubjectAddForm()
    if form.validate_on_submit():
        subject = Subject(subject=form.subject.data,
                          description=form.description.data)
        try:
            # add department to the database
            db.session.add(subject)
            db.session.commit()
            flash('Вы успешно добавили предмет.')
        except:
            # in case department name already exists
            flash('Ошибка: предмет существует.')
        return redirect(url_for('admin.subjects'))

    return render_template('admin/subject_add.html', form=form, title='Добавить предмет')


@admin.route('/admin/choice/<int:id>/add', methods=['GET', 'POST'])
@login_required
def choice_add(id):
    check_admin()

    subject = Subject.query.get_or_404(id)

    form = ChoiceAddForm()
    if form.validate_on_submit():
        choice = TrainingChoice(
            number=form.number.data,
            description=form.description.data, subject_id=id)
        if not TrainingChoice.query.filter(
                        (TrainingChoice.number == choice.number) & (
                            TrainingChoice.subject_id == choice.subject_id)).all():
            try:
                db.session.add(choice)
                db.session.commit()
                flash('Вы успешно добавили тип задания.')
            except:
                flash('Ошибка: тип задания существует.')
        else:
            flash('Задание существует')
        return redirect(url_for('admin.subject', id=id))

    return render_template('admin/choice_add.html', form=form, subject=subject, title='Добавить тип заданий')


@admin.route('/admin/choice/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def choice_edit(id):
    check_admin()

    choice = TrainingChoice.query.get_or_404(id)
    subject = Subject.query.get_or_404(choice.subject_id)

    form = ChoiceEditForm(obj=choice)
    if form.validate_on_submit():
        choice.description = form.description.data
        try:
            db.session.commit()
        except:
            flash('Ошибка')
        return redirect(url_for('admin.subject', id=choice.subject_id))
    return render_template('admin/choice_edit.html', subject=subject, form=form, methods=['GET', 'POST'])


@admin.route('/admin/choice/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def choice_delete(id):
    check_admin()

    choice = TrainingChoice.query.get_or_404(id)
    try:
        db.session.delete(choice)
        db.session.commit()
        flash('Удалено')
    except:
        flash('Ошибка')
    return redirect(url_for('admin.subject', id=choice.subject_id))


@admin.route('/admin/task/<int:id>/add', methods=['GET', 'POST'])
@login_required
def task_add(id):
    check_admin()

    subject = Subject.query.get_or_404(id)

    form = TaskAddForm()
    if form.validate_on_submit():
        task = Task(number=form.number.data, text=form.question.data,
                    right_answer=form.answer.data, subject_id=id)
        try:
            db.session.add(task)
            db.session.commit()
            flash('Вы успешно добавили задание.')
        except:
            flash('Ошибка.')
        return redirect(url_for('admin.subject', id=id))
    return render_template('admin/task_add.html', form=form, subject=subject, title='Добавить задание')


@admin.route('/admin/student/<int:id>', methods=['GET', 'POST"'])
@login_required
def student(id):
    check_admin()

    student = Client.query.get_or_404(id)
    if student.status != 1:
        flash('Это не ученик')
        return redirect(url_for('admin.clients'))

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    schedule = Schedule.query.filter((Schedule.client_id == id) & (Schedule.time > datetime.datetime.now())).all()

    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
              'декабря']

    for schedule_item in schedule:
        schedule_item.day = schedule_item.time.day
        schedule_item.subject_name = Subject.query.get_or_404(schedule_item.subject_id).subject
        schedule_item.dow = schedule_item.time.weekday()
        schedule_item.day_of_week = weekdays[schedule_item.dow]
        schedule_item.date = str(schedule_item.time.day) + ' ' + months[
            schedule_item.time.month - 1] + ' ' + str(schedule_item.time.year)
        schedule_teacher = Client.query.get_or_404(Teacher.query.get_or_404(schedule_item.teacher_id).login_id)
        schedule_item.teacher_name = schedule_teacher.last_name + ' ' + schedule_teacher.first_name[0] + '. ' + \
                                     schedule_teacher.middle[0] + '.'

    now = datetime.datetime.now()
    byweeks = [[[], [], [], [], [], [], []]]
    endweek = now + datetime.timedelta(days=(7 - now.weekday()))
    endweek = endweek.replace(hour=0, minute=0, second=0, microsecond=0)
    for schedule_item in schedule:
        if schedule_item.time < endweek:
            byweeks[0][schedule_item.dow].append(schedule_item)
        else:
            try:
                byweeks[(schedule_item.time - endweek).days // 7 + 1][schedule_item.dow].append(schedule_item)
            except IndexError:
                for _ in range(((schedule_item.time - endweek).days // 7 + 1) - len(byweeks) + 1):
                    byweeks.append([[], [], [], [], [], [], []])
                byweeks[(schedule_item.time - endweek).days // 7 + 1][schedule_item.dow].append(schedule_item)

    return render_template('admin/student.html', student=student, schedule=byweeks, weekdays=weekdays,
                           title=(student.last_name + student.first_name + student.middle))


@admin.route('/admin/teacher/<int:id>', methods=['GET', 'POST'])
@login_required
def teacher(id):
    check_admin()

    teacher = Client.query.get_or_404(id)
    if teacher.status != 3:
        flash('Это не учитель')
        return redirect(url_for('admin.clients'))

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    schedule = Schedule.query.filter((Schedule.teacher_id == id) & (Schedule.time > datetime.datetime.now())).all()

    for schedule_item in schedule:
        schedule_item.day = schedule_item.time.day
        schedule_item.subject_name = Subject.query.get_or_404(schedule_item.subject_id).subject
        schedule_item.dow = schedule_item.time.weekday()
        schedule_item.day_of_week = weekdays[schedule_item.dow]
        schedule_item.date = awesome_date(schedule_item.time)
        schedule_student = Client.query.get_or_404(Client.query.get_or_404(schedule_item.client_id).login_id)
        schedule_item.student = schedule_student.last_name + ' ' + schedule_student.first_name[0] + '. ' + \
                                schedule_student.middle[0] + '.'

    now = datetime.datetime.now()
    byweeks = [[[], [], [], [], [], [], []]]
    endweek = now + datetime.timedelta(days=(7 - now.weekday()))
    endweek = endweek.replace(hour=0, minute=0, second=0, microsecond=0)
    for schedule_item in schedule:
        if schedule_item.time < endweek:
            byweeks[0][schedule_item.dow].append(schedule_item)
        else:
            try:
                byweeks[(schedule_item.time - endweek).days // 7 + 1][schedule_item.dow].append(schedule_item)
            except IndexError:
                for _ in range(((schedule_item.time - endweek).days // 7 + 1) - len(byweeks) + 1):
                    byweeks.append([[], [], [], [], [], [], []])
                byweeks[(schedule_item.time - endweek).days // 7 + 1][schedule_item.dow].append(schedule_item)

    return render_template('admin/teacher.html', schedule=byweeks, weekdays=weekdays, teacher=teacher,
                           title=(teacher.last_name + teacher.first_name + teacher.middle))


@admin.route('/admin/materials', methods=['GET', 'POST'])
@login_required
def materials():
    check_admin()

    materials = Material.query.all()

    for material in materials:
        material.date_t = awesome_date(material.date)
        teacher = Client.query.get_or_404(Teacher.query.get_or_404(material.teacher_id).login_id)
        material.teacher_name = teacher.first_name + ' ' + teacher.last_name

    return render_template('admin/materials.html', materials=materials, title='Материалы')


@admin.route('/admin/salaries')
@login_required
def salary():
    check_admin()

    salaries = Salary.query.all()
    return render_template('admin/salaries.html', salaries=salaries, title='Зарплата')


@admin.route('/admin/salary/<int:id>/pay', methods=['GET', 'POST'])
@login_required
def salary_pay(id):
    check_admin()

    teacher = Client.query.get_or_404(id)
    form = SalaryForm()
    if form.validate_on_submit():
        salary = Salary(amount=form.amount.data,
                        description=form.description.data, date=datetime.datetime.now())
        try:
            db.session.add(salary)
            db.session.commit()
        except:
            flash('Ошибка')
        return redirect(url_for('admin.teacher', id=id))

    return render_template('admin/salary_pay.html', teacher=teacher, form=form, methods=['GET', 'POST'])


@admin.route('/admin/material/add', methods=['GET', 'POST'])
@login_required
def add_material():
    check_admin()
    form = AddMaterial()
    if form.validate_on_submit():
        teacher = Client.query.filter(
            (Client.first_name == form.first_name.data) & (Client.last_name == form.last_name.data) & (
                Client.status == 3)).first()
        print(teacher)
        subject = Subject.query.filter(Subject.subject == form.subject.data).first()
        teacher.tid = Teacher.query.filter(Teacher.login_id == teacher.id).first().id
        subject
        if teacher:
            material = Material(teacher_id=teacher.tid, subject_id=subject.id, date = form.date.data)
            try:
                db.session.add(material)
                db.session.commit()
                flash('Вы успешно добавили материал.')
            except:
                # in case department name already exists
                flash('Ошибка.')
            return redirect(url_for('admin.materials'))

    return render_template('admin/add_material.html', form=form, title='Добавить материалы')
