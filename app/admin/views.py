from flask import flash, redirect, render_template, url_for, abort
from flask_login import login_required, current_user

from . import admin
from ..models import Client
from .. import db


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
    list_clients = Client.query.all()
    return render_template('admin/clients.html', clients=list_clients, title='Клиенты')


@admin.route('/admin/subjects')
@login_required
def subjects():
    check_admin()
    list_subjects = Client.query.all()
    return render_template('admin/subjects.html', subjects=list_subjects, title='Клиенты')
