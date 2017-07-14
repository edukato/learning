from flask import flash, redirect, render_template, url_for, abort, request
from flask_login import login_required, current_user

import datetime

from . import teacher
from ..models import Client, RoadMap
from ..models import Client, Schedule, Subject
from .. import db


def check_teacher():
    if not (current_user.status == 3):
        abort(403)


@teacher.route('/teacher')
@login_required
def dashboard():
    check_teacher()
    clients = Client.query.filter(Client.mentor == current_user.id).all()
    return render_template('teacher/dashboard.html', clients=clients, title='Главная страница')


@teacher.route('/teacher/students')
@login_required
def students():
    check_teacher()
    return render_template('teacher/students.html', title='Ваши ученики')


@teacher.route('/teacher/salary')
@login_required
def salary():
    check_teacher()
    return render_template('teacher/salary.html', title='Зарплата')


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
        return render_template('teacher/change_roadmap.html', student_id = id, laststep = ((road_map_items[-1].step)+1), road_map_items=road_map_items, title='Изменение roadmap')
    except IndexError:
        return render_template('teacher/change_roadmap.html', student_id = id, laststep = 1, title='Изменение roadmap')


@teacher.route('/teacher/add_step/<int:id>', methods=['GET', 'POST'])
@login_required
def add_step(id):
    check_teacher()
    try:
        road_map_items = RoadMap.query.filter(RoadMap.client_id == id).order_by(
            RoadMap.step.asc()).all()
        laststep = ((road_map_items[-1].step) + 1)
        new_step = RoadMap(client_id = id, step = laststep, name = request.form['heading_new'], description = request.form['description_new'] , if_done = False)
    except IndexError:
        laststep = 1
        new_step = RoadMap(client_id=id, step=laststep, name=request.form['heading_new'],
                           description=request.form['description_new'], if_done=False)
    db.session.add(new_step)
    db.session.commit()
    return redirect(url_for('teacher.change_roadmap', id = id))

@teacher.route('/teacher/change_roadmap_redaction/<int:id>/<int:step>', methods=['GET', 'POST'])
@login_required
def change_roadmap_redaction(id, step):
    check_teacher()
    road_map_items = RoadMap.query.filter(RoadMap.client_id == id).order_by(
        RoadMap.step.asc()).all()
    return render_template('teacher/change_roadmap_redaction.html', step = step, student_id = id, laststep = ((road_map_items[-1].step)+1), road_map_items=road_map_items, title='Изменение roadmap')

@teacher.route('/teacher/change_step/<int:id>/<int:step_for_change>', methods=['GET', 'POST'])
@login_required
def change_step(id, step_for_change):
    check_teacher()

    db.session.query(RoadMap).filter(RoadMap.client_id == id).filter(RoadMap.step == step_for_change).update({"name": (request.form['heading_edit']), "description": (request.form['description_edit'])})
    db.session.commit()

    return redirect(url_for('teacher.change_roadmap', id = id))

@teacher.route('/teacher/delete_step/<int:id>/<int:step_for_delete>', methods=['GET', 'POST'])
@login_required
def delete_step(id, step_for_delete):
    check_teacher()

    road_map_items = RoadMap.query.filter(RoadMap.client_id == id).order_by(
        RoadMap.step.asc()).all()
    laststep = ((road_map_items[-1].step) + 1)
    RoadMap.query.filter(RoadMap.client_id == id).filter(RoadMap.step == step_for_delete).delete()
    for i in range(laststep-step_for_delete):
        RoadMap.query.filter(RoadMap.client_id == id).filter(RoadMap.step == step_for_delete + i + 1).update({"step": step_for_delete +i })

    db.session.commit()

    return redirect(url_for('teacher.change_roadmap', id=id))

@teacher.route('/teacher/student/<int:id>', methods=['GET', 'POST'])
@login_required
def show_student(id):
    student = Client.query.get_or_404(id)
    if student.mentor != current_user.id:
        abort(403)
    return render_template('teacher/student.html',
                           student=student, title="ученик")

@teacher.route('/teacher/schedule/<int:id>', methods=['GET', 'POST'])
@login_required
def get_schedule(id):
    check_teacher()

    student = Client.query.get_or_404(id)
    if student.mentor != current_user.id:
        abort(403)

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    schedule = Schedule.query.filter((Schedule.client_id == id) & (Schedule.time > datetime.datetime.now())).all()

    for schedule_item in schedule:
        schedule_item.day = schedule_item.time.day
        schedule_item.subject_name = Subject.query.get_or_404(schedule_item.subject_id).subject
        schedule_item.dow = schedule_item.time.weekday()
        schedule_item.day_of_week = weekdays[schedule_item.dow]

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

    return render_template('teacher/schedule.html', weekdays=weekdays, student=student, schedule=byweeks, title='Расписание')
    return render_template('teacher/schedule.html', weekdays=weekdays, student=student, schedule=byweeks,
                           title='Расписание')
