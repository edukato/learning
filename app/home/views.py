# app/home/views.py

from flask import flash, redirect, render_template, url_for, abort
from flask_login import login_required, current_user

from . import home
from .. import db


@home.route('/')
def homepage():
    return render_template('home/index.html', title="Добро пожаловать в edukato!")


@home.route('/account')
@login_required
def account():
    return render_template('home/account.html', title="Мой аккаунт")


@home.route('/feed')
@login_required
def account():
    return render_template('home/feed.html', title="Лента")


@home.route('/support')
@login_required
def account():
    return render_template('home/support.html', title="Поддержка")


@home.route('/shop')
@login_required
def account():
    return render_template('home/shop.html', title="Магазин")


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