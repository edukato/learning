# app/home/views.py

import datetime, os

from flask import flash, redirect, render_template, url_for
from flask_login import login_required, current_user

from . import home
from ..models import Service, SellingLog, Client
from .. import db
from .forms import AccountEditForm


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


@home.route('/shop')
@login_required
def shop():
    services_0 = Service.query.filter(
        (Service.expiration_date > datetime.datetime.now()) & (
            Service.start_date < datetime.datetime.now()) & (Service.type == '0')).all()
    services_0_count = Service.query.filter(
        (Service.expiration_date > datetime.datetime.now()) & (
            Service.start_date < datetime.datetime.now()) & (Service.type == '0')).count()
    services_1 = Service.query.filter(
        (Service.expiration_date > datetime.datetime.now()) & (
            Service.start_date < datetime.datetime.now()) & (Service.type == '1')).all()
    services_1_count = Service.query.filter(
        (Service.expiration_date > datetime.datetime.now()) & (
            Service.start_date < datetime.datetime.now()) & (Service.type == '1')).count()
    services_2 = Service.query.filter(
        (Service.expiration_date > datetime.datetime.now()) & (
            Service.start_date < datetime.datetime.now()) & (Service.type == '2')).all()
    services_2_count = Service.query.filter(
        (Service.expiration_date > datetime.datetime.now()) & (
            Service.start_date < datetime.datetime.now()) & (Service.type == '2')).count()
    return render_template('home/shop.html', services_0=services_0, services_0_count=services_0_count,
                           services_1=services_1, services_1_count=services_1_count, services_2=services_2,
                           services_2_count=services_2_count, title="Магазин")


@home.route('/pay')
@login_required
def pay():
    return render_template('home/pay.html', title="Пополнение счёта")


@home.route('/training')
@login_required
def training():
    return render_template('home/train/training.html', title="Тренировка")


@home.route('/recommendation')
@login_required
def recommendation():
    return render_template('home/train/recommendation.html', title="Рекомендуем отработать")


@home.route('/ege')
@login_required
def ege():
    return render_template('home/train/ege.html', title="Вариант ЕГЭ")


@home.route('/help')
@login_required
def help():
    return render_template('home/help.html', title="Служба поддержки")


@home.route('/contacts')
@login_required
def contacts():
    return render_template('home/contacts.html', title="Контакты")


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
                           service=service, title="Показать услугу")


@home.route('/account/edit', methods=['GET', 'POST'])
@login_required
def edit_account():
    client = Client.query.get_or_404(current_user.id)

    form = AccountEditForm(obj=client)
    if form.validate_on_submit():
        client.first_name = form.first_name.data
        client.last_name = form.last_name.data
        client.password = form.password.data
        if form.photo.data is not None:
            form.photo.data.save('app/static/images/profile/' + str(current_user.id) + '.png')
        db.session.commit()
        flash('Ваше задание выполнено, капитан.')
        return redirect(url_for('home.account'))

    form.first_name.data = client.first_name
    form.last_name.data = client.last_name

    return render_template('home/change_pers_inf.html', form=form,
                           client=client, title="Изменение персональных данных")


@home.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    alltransactions = SellingLog.query.filter(SellingLog.client_id == current_user.id).all()
    for transaction in alltransactions:
        transaction.name = (Service.query.filter(Service.id == transaction.service_id).first()).name
    return render_template('home/transactions.html', transactions=alltransactions, title='Транзакции')


@home.route('/road_map', methods=['GET','POST'])
@login_required
def road_map():
    return render_template('home/road_map.html', title='Дорожная карта')