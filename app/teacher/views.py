from flask import flash, redirect, render_template, url_for, abort
from flask_login import login_required, current_user

from . import teacher
from ..models import Client, RoadMap
from .. import db


def check_teacher():
    if not (current_user.status == 3):
        abort(403)


@teacher.route('/teacher')
@login_required
def dashboard():
    check_teacher()
    return render_template('teacher/dashboard.html', title='Главная страница')


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
    client = Client.query.get_or_404(id)
    road_map_items = RoadMap.query.filter(RoadMap.client_id == id).order_by(
        RoadMap.step.asc()).all()
    return render_template('teacher/change_roadmap.html', road_map_items=road_map_items, title='Изменение roadmap')