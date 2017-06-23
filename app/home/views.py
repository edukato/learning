# app/home/views.py

import datetime

from flask import flash, redirect, render_template, url_for, abort
from flask_login import login_required, current_user

from . import home
from ..models import Service,SellingLog
from .. import db


@home.route('/')
def homepage():
    return render_template('home/index.html', title="Добро пожаловать в edukato!")


@home.route('/account')
@login_required
def account():
    active_services = SellingLog.query.filter((SellingLog.client_id == current_user.id)&(SellingLog.access_start < datetime.datetime.now())&(SellingLog.access_end > datetime.datetime.now())).all()
    for service in active_services:
        service_info = Service.query.get_or_404(service.service_id)
        service.name = service_info.name
        service.description = service_info.description

    return render_template('home/account.html', active_services=active_services, title="Мой аккаунт")


@home.route('/feed')
@login_required
def feed():
    return render_template('home/feed.html', title="Лента")


@home.route('/support')
@login_required
def support():
    return render_template('home/support.html', title="Поддержка")


@home.route('/shop')
@login_required
def shop():
    services = Service.query.filter((Service.expiration_date > datetime.datetime.now()) & (Service.start_date < datetime.datetime.now())).all()
    return render_template('home/shop.html', services=services, title="Магазин")


@home.route('/shop/show/<int:id>', methods=['GET', 'POST'])
@login_required
def show_experiment(id):
    service = Service.query.get_or_404(id)
    if service.user_id != current_user.id:
        abort(403)
    service.content = Markup(markdown(experiment.content,['markdown.extensions.extra']))
    return render_template('home/shop/service.html',
                           action_project='show_service',
                           service=service, title="Показать услушу")