# app/home/views.py

import datetime

from flask import flash, redirect, render_template, url_for, abort
from flask_login import login_required, current_user

from . import home
from ..models import Service, SellingLog
from .. import db


@home.route('/')
def homepage():
    if current_user.is_authenticated:
        return redirect(url_for('home.account'))
    else:
        return render_template('home/index.html', title="Добро пожаловать в edukato!")


@home.route('/account')
@login_required
def account():
    active_services = SellingLog.query.filter(
        (SellingLog.client_id == current_user.id) & (SellingLog.access_start < datetime.datetime.now()) & (
            SellingLog.access_end > datetime.datetime.now())).all()
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
    services = Service.query.filter(
        (Service.expiration_date > datetime.datetime.now()) & (Service.start_date < datetime.datetime.now())).all()
    return render_template('home/shop.html', services=services, title="Магазин")


@home.route('/shop/confirm/<int:id>', methods=['GET', 'POST'])
@login_required
def confirm_transaction(id):
    service = Service.query.get_or_404(id)

    # Когда-нибудь проверить несовпадение дат

    return render_template('home/confirm_transaction.html', service=service, title="Подтверждение транзакции")


@home.route('/shop/confirmed/<int:id>', methods=['GET', 'POST'])
@login_required
def confirmed_transaction(id):
    service = Service.query.get_or_404(id)
    transaction = SellingLog(client_id=current_user.id, service_id=id, date_time=datetime.datetime.now(),
                             access_start=datetime.datetime.now(), access_end=service.expiration_date)
    db.session.add(transaction)
    db.session.commit()
    flash('Поздравляем с покупкой!')
    return redirect(url_for('home.account'))


@home.route('/shop/show/<int:id>', methods=['GET', 'POST'])
@login_required
def show_service(id):
    service = Service.query.get_or_404(id)
    return render_template('home/service.html',
                           service=service, title="Показать услушу")
