from flask import flash, redirect, render_template, url_for, abort
from flask_login import login_required, current_user

import datetime

from . import teacher
<<<<<<< HEAD
from ..models import Client, RoadMap
=======
from ..models import Client, Schedule, Subject
>>>>>>> 5f778fc6649ce83d696506115950c27a74ad79d3
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

<<<<<<< HEAD
@teacher.route('/teacher/change_roadmap/<int:id>', methods=['GET', 'POST'])
@login_required
def change_roadmap(id):
    check_teacher()
    client = Client.query.get_or_404(id)
    road_map_items = RoadMap.query.filter(RoadMap.client_id == id).order_by(
        RoadMap.step.asc()).all()
    return render_template('teacher/change_roadmap.html', road_map_items=road_map_items, title='Изменение roadmap')
=======

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
>>>>>>> 5f778fc6649ce83d696506115950c27a74ad79d3
