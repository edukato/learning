from flask import flash, redirect, render_template, url_for, abort, request
from flask_login import login_required, current_user

import datetime

from . import teacher
from ..models import Client, RoadMap
from ..models import Client, Schedule, Subject, OperatingSchedules, Teacher, Salary, Material, Skil
from .. import db
from .forms import MaterialEditForm
from ..utils import awesome_date


def check_teacher():
    if not (current_user.status == 3):
        abort(403)


@teacher.route('/teacher')
@login_required
def dashboard():
    check_teacher()
    clients = Client.query.filter(Client.mentor == current_user.id).all()
    schedule = Schedule.query.filter(
        (Schedule.teacher_id == Teacher.query.filter(Teacher.login_id == current_user.id).first().id) & (
            Schedule.time >= (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)))).all()

    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
              'декабря']

    for schedule_item in schedule:
        schedule_item.date = str(schedule_item.time.day) + ' ' + months[
            schedule_item.time.month - 1] + ' ' + str(schedule_item.time.year)
        schedule_item.subject_name = Subject.query.get_or_404(schedule_item.subject_id).subject
        schedule_student = Client.query.get_or_404(schedule_item.client_id)
        schedule_item.student_name = schedule_student.last_name + ' ' + schedule_student.first_name[0] + '. ' + \
                                     schedule_student.middle[0] + '.'

    return render_template('teacher/dashboard.html', schedule=schedule[0:5], clients=clients, title='Главная страница')


@teacher.route('/teacher/students')
@login_required
def students():
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
              'декабря']

    check_teacher()

    mentorship = Client.query.filter(Client.mentor == current_user.id).all()

    schedule_after = Schedule.query.filter(
        (Schedule.teacher_id == Teacher.query.filter(Teacher.login_id == current_user.id).first().id) & (
            Schedule.time >= (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)))).order_by(
        Schedule.time.asc()).all()

    schedule_before = Schedule.query.filter(
        (Schedule.teacher_id == Teacher.query.filter(Teacher.login_id == current_user.id).first().id) & (
            Schedule.time < (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)))).order_by(
        Schedule.time.desc()).all()

    schedule_after_1 = []
    for schedule_after_item in schedule_after:
        i = True
        if schedule_after_1:
            for schedule_after_item_inner in schedule_after_1:
                if schedule_after_item_inner.client_id == schedule_after_item.client_id:
                    i = False
        if i:
            schedule_after_1.append(schedule_after_item)

    schedule_before_1 = []
    for schedule_before_item in schedule_before:
        i = True
        if schedule_before_1:
            for schedule_before_item_inner in schedule_before_1:
                if schedule_before_item_inner.client_id == schedule_before_item.client_id:
                    i = False
        if i:
            schedule_before_1.append(schedule_before_item)

    for schedule_after_item in schedule_after_1:
        schedule_after_item_client = Client.query.get_or_404(schedule_after_item.client_id)
        schedule_after_item.date = awesome_date(schedule_after_item.time)
        schedule_after_item.client_name = schedule_after_item_client.last_name + ' ' + \
                                          schedule_after_item_client.first_name + ' ' + \
                                          schedule_after_item_client.middle

    for schedule_before_item in schedule_before_1:
        schedule_before_item_client = Client.query.get_or_404(schedule_before_item.client_id)
        schedule_before_item.date = awesome_date(schedule_before_item.time)
        schedule_before_item.client_name = schedule_before_item_client.last_name + ' ' + \
                                           schedule_before_item_client.first_name + ' ' + \
                                           schedule_before_item_client.middle
    return render_template('teacher/students.html', schedule_after=schedule_after_1, schedule_before=schedule_before_1,
                           mentorship=mentorship, title='Ваши ученики')


@teacher.route('/teacher/salary')
@login_required
def salary():
    check_teacher()

    teacher = Teacher.query.filter(Teacher.login_id == current_user.id).first()
    salaries = Salary.query.filter(Salary.teacher_id == teacher.id).all()
    return render_template('teacher/salary.html', salaries=salaries, title='Зарплата')


@teacher.route('/teacher/help')
@login_required
def help():
    check_teacher()
    return render_template('teacher/help.html', title='Поддержка')


@teacher.route('/teacher/change_roadmap/<int:id>', methods=['GET', 'POST'])
@login_required
def change_roadmap(id):
    check_teacher()
    try:
        road_map_items = RoadMap.query.filter(RoadMap.client_id == id).order_by(
            RoadMap.step.asc()).all()
        return render_template('teacher/change_roadmap.html', student_id=id, laststep=((road_map_items[-1].step) + 1),
                               road_map_items=road_map_items, title='Изменение roadmap')
    except IndexError:
        return render_template('teacher/change_roadmap.html', student_id=id, laststep=1, title='Изменение roadmap')


@teacher.route('/teacher/add_step/<int:id>', methods=['GET', 'POST'])
@login_required
def add_step(id):
    check_teacher()
    try:
        road_map_items = RoadMap.query.filter(RoadMap.client_id == id).order_by(
            RoadMap.step.asc()).all()
        laststep = ((road_map_items[-1].step) + 1)
        new_step = RoadMap(client_id=id, step=laststep, name=request.form['heading_new'],
                           description=request.form['description_new'], if_done=False)
    except IndexError:
        laststep = 1
        new_step = RoadMap(client_id=id, step=laststep, name=request.form['heading_new'],
                           description=request.form['description_new'], if_done=False)
    db.session.add(new_step)
    db.session.commit()
    return redirect(url_for('teacher.change_roadmap', id=id))


@teacher.route('/teacher/change_roadmap_redaction/<int:id>/<int:step>', methods=['GET', 'POST'])
@login_required
def change_roadmap_redaction(id, step):
    check_teacher()
    road_map_items = RoadMap.query.filter(RoadMap.client_id == id).order_by(
        RoadMap.step.asc()).all()
    return render_template('teacher/change_roadmap_redaction.html', step=step, student_id=id,
                           laststep=((road_map_items[-1].step) + 1), road_map_items=road_map_items,
                           title='Изменение roadmap')


@teacher.route('/teacher/change_step/<int:id>/<int:step_for_change>', methods=['GET', 'POST'])
@login_required
def change_step(id, step_for_change):
    check_teacher()

    db.session.query(RoadMap).filter(RoadMap.client_id == id).filter(RoadMap.step == step_for_change).update(
        {"name": (request.form['heading_edit']), "description": (request.form['description_edit'])})
    db.session.commit()

    return redirect(url_for('teacher.change_roadmap', id=id))


@teacher.route('/teacher/delete_step/<int:id>/<int:step_for_delete>', methods=['GET', 'POST'])
@login_required
def delete_step(id, step_for_delete):
    check_teacher()

    road_map_items = RoadMap.query.filter(RoadMap.client_id == id).order_by(
        RoadMap.step.asc()).all()
    laststep = ((road_map_items[-1].step) + 1)
    RoadMap.query.filter(RoadMap.client_id == id).filter(RoadMap.step == step_for_delete).delete()
    for i in range(laststep - step_for_delete):
        RoadMap.query.filter(RoadMap.client_id == id).filter(RoadMap.step == step_for_delete + i + 1).update(
            {"step": step_for_delete + i})

    db.session.commit()

    return redirect(url_for('teacher.change_roadmap', id=id))


@teacher.route('/teacher/student/<int:id>', methods=['GET', 'POST'])
@login_required
def show_student(id):
    check_teacher()
    student = Client.query.get_or_404(id)
    if (student.subjects != None):
        subjects_id = student.subjects.split(",")
        subjects = []
        for subject_id in subjects_id:
            subjects.append(Subject.query.get_or_404(int(subject_id)))
    else:
        subjects = []

    if student.mentor != current_user.id:
        abort(403)
    return render_template('teacher/student.html',
                           student=student, subjects = subjects, title="ученик")

@teacher.route('/teacher/student/<int:id>/add_subject/', methods=['GET', 'POST'])
@login_required
def add_subject(id):
    check_teacher()
    student = Client.query.get_or_404(id)
    subject_name = request.form['subject_name']
    subject = Subject.query.filter(Subject.subject == subject_name).first()
    add = True

    if(student.subjects != None):
        student_subjects = student.subjects.split(",")
    else:
        student_subjects = []

    if(subject != None):
        for student_subject in student_subjects:
            if(subject.id == int(student_subject)):
                add = False

    if (subject != None and add == True):
        if (student.subjects != None):
            old_subjects = student.subjects
            new_subjects = str(old_subjects) + "," + str(subject.id)
        else:
            old_subjects = ""
            new_subjects = str(subject.id)

        student.subjects = new_subjects
        for i in range(subject.tasks_number):
            new_skil = Skil(client_id = id, subject = subject.id, number = i+1, level = 1, right_percent = 0, answers_amount = 0)
            db.session.add(new_skil)
        db.session.commit()
        flash("Оки-доки")
    elif (subject != None and add == False):
        flash("Данный предмет уже присутствует в списке! Разуй глаза, блеать!")
    else:
        flash("В базе данных нет предмета с указанным названием")

    return redirect(url_for('teacher.show_student', id=int(request.form['student_id']), title="ученик"))

@teacher.route('/teacher/student/<int:id>/delete_subject/<int:subject_id>', methods=['GET','POST'])
@login_required
def delete_subject(id, subject_id):
    check_teacher()
    student = Client.query.get_or_404(id)
    subject = Subject.query.get_or_404(subject_id)
    student_subjects_id = str(student.subjects).split(",")
    new_student_subjects_id = []
    new_student_subjects = ""
    for student_subject_id in student_subjects_id:
        if(subject_id  != int(student_subject_id)):
            new_student_subjects_id.append(student_subject_id)

    for student_subject_id in new_student_subjects_id:
        if (new_student_subjects != ""):
            new_student_subjects = new_student_subjects + "," + str(student_subject_id)
        else:
            new_student_subjects = str(student_subject_id)

    if(new_student_subjects != ""):
        student.subjects = new_student_subjects
    else:
        student.subjects = None

    rows_for_delete = Skil.query.filter(Skil.client_id == id).filter(Skil.subject == subject_id).all()

    for i in range(subject.tasks_number):
        db.session.delete(rows_for_delete[i])

    db.session.commit()

    return redirect(url_for('teacher.show_student', id=student.id, title="ученик"))

@teacher.route('/teacher/schedule/<int:id>', methods=['GET', 'POST'])
@login_required
def get_schedule(id):
    check_teacher()

    student = Client.query.get_or_404(id)
    if student.mentor != current_user.id:
        abort(403)

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

    return render_template('teacher/schedule.html', weekdays=weekdays, student=student, schedule=byweeks,
                           title='Расписание')


@teacher.route('/teacher/schedule/remove/<int:id>', methods=['GET', 'POST'])
def remove_sch_item(id):
    check_teacher()

    schedule_item = Schedule.query.get_or_404(id)
    student = Client.query.get_or_404(schedule_item.client_id)
    if student.mentor != current_user.id:
        abort(403)
    subject = Subject.query.get_or_404(schedule_item.subject_id)
    teacher = Client.query.get_or_404(schedule_item.teacher_id)

    return render_template('teacher/remove_sch_item.html', teacher=teacher, subject=subject, student=student,
                           schedule_item=schedule_item, title='Подтвердите удаление')


@teacher.route('/teacher/schedule/delete/<int:id>', methods=['GET', 'POST'])
def really_remove(id):
    check_teacher()

    schedule_item = Schedule.query.get_or_404(id)
    student = Client.query.get_or_404(schedule_item.client_id)
    if student.mentor != current_user.id:
        abort(403)
    print(schedule_item.id)
    Schedule.query.filter(Schedule.id == schedule_item.id).delete()
    db.session.commit()
    return redirect(url_for('teacher.get_schedule', id=schedule_item.client_id))


@teacher.route('/teacher/addition/<int:client_id>/<int:week>/<int:id>')
@login_required
def schedule_addition(client_id, week, id):
    check_teacher()

    student = Client.query.get_or_404(client_id)
    if student.mentor != current_user.id:
        abort(403)
    now_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    op_schedule = OperatingSchedules.query.get_or_404(id)
    schedule_item = Schedule(client_id=client_id, teacher_id=current_user.id, subject_id=op_schedule.subject_id,
                             time=(now_day + datetime.timedelta(
                                 days=(week * 7 - now_day.weekday() + op_schedule.day_of_the_week))),
                             interval_number=op_schedule.interval_number)
    db.session.add(schedule_item)
    db.session.commit()
    return redirect(url_for('teacher.get_schedule', id=client_id))


@teacher.route('/teacher/add/<int:id>', methods=['GET', 'POST'])
@login_required
def schedule_add(id):
    check_teacher()

    student = Client.query.get_or_404(id)
    if student.mentor != current_user.id:
        abort(403)

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    opschedule = OperatingSchedules.query.all()

    now = datetime.datetime.now()
    endweek = now + datetime.timedelta(days=(7 - now.weekday()))
    endweek = endweek.replace(hour=0, minute=0, second=0, microsecond=0)

    week = [[], [], [], [], [], [], []]
    for opschedule_item in opschedule:
        opschedule_item.subject_name = Subject.query.get_or_404(opschedule_item.subject_id).subject
        opsch_teacher_id = Teacher.query.get_or_404(opschedule_item.teacher_id).login_id
        opsch_teacher = Client.query.get_or_404(opsch_teacher_id)
        opschedule_item.teacher_name = opsch_teacher.last_name + ' ' + opsch_teacher.first_name + ' ' + opsch_teacher.middle
        week[opschedule_item.day_of_the_week].append(opschedule_item)

    byweeks = list()
    byweeks.append(week[:])
    byweeks.append(week[:])
    byweeks.append(week[:])

    for i in range(0, now.weekday()):
        byweeks[0][i] = [][:]

    now_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    day_counter = 0

    for week in byweeks:
        for day in week:
            day_counter += 1
            for schedule_item in day:
                if Schedule.query.filter((Schedule.time == (now_day + datetime.timedelta(days=day_counter))) & (
                            Schedule.interval_number == schedule_item.interval_number)).all() is None:
                    schedule_item.remove()

    return render_template('teacher/teachers_schedule.html', student=student, weekdays=weekdays, byweeks=byweeks,
                           title='Добавить элемент')


@teacher.route('/teacher/material/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_material(id):
    check_teacher()

    material = Material.query.get_or_404(id)

    form = MaterialEditForm(obj=material)
    if form.validate_on_submit():
        material.title = form.title.data
        material.description = form.description.data
        material.text = form.text.data
        db.session.commit()
        return redirect(url_for('teacher.materials'))

    form.title.data = material.title
    form.description.data = material.description
    form.text.data = material.text
    return render_template('teacher/edit_material.html', form=form, title='Изменить материал')


@teacher.route('/teacher/material', methods=['GET', 'POST'])
@login_required
def materials():
    check_teacher()

    materials = Material.query.filter(
        Material.teacher_id == Teacher.query.filter(Teacher.login_id == current_user.id).first().id).all()

    for material in materials:
        material.date_t = awesome_date(material.date)

    return render_template('teacher/materials.html', materials=materials, title='Материалы')


@teacher.route('/teacher/material/<int:id>', methods=['GET', 'POST'])
@login_required
def material(id):
    check_teacher()

    material = Material.query.get_or_404(id)
    if Teacher.query.get_or_404(material.teacher_id).login_id != current_user.id:
        abort(403)

    material.date_t = awesome_date(material.date)
    return render_template('teacher/material.html', material=material, title='Материал')