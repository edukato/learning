from flask import flash, redirect, render_template, url_for, abort
from flask_login import login_required, current_user

from . import admin
from ..models import Client, Subject, TrainingChoice, Task
from .. import db
from .forms import SubjectEditForm, SubjectAddForm, ChoiceAddForm, ChoiceEditForm, TaskAddForm


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
        task = Task(text=form.question.data,
            right_answer=form.answer.data, subject_id=id)
        try:
            db.session.add(task)
            db.session.commit()
            flash('Вы успешно добавили задание.')
        except:
            flash('Ошибка.')
        return redirect(url_for('admin.subject', id=id))
    return render_template('admin/task_add.html', form=form, subject=subject, title='Добавить задание')
