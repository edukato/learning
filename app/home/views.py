# app/home/views.py

import datetime, os, random

from numpy import random

from flask import flash, redirect, render_template, url_for, abort, request
from flask_login import login_required, current_user

from . import home
<<<<<<< HEAD
from ..models import Service, SellingLog, Client, RoadMap, TasksError, Subject
=======
from ..models import Service, SellingLog, Client, RoadMap, TasksError, TrainingRecommendationSession, Answer, \
    TrainingChoice, Task
>>>>>>> ed22cb2fd4322d5e7f41a7ae9f6fcfad9dc67b42
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
    if current_user.status == 2:
        return redirect(url_for('admin.dashboard'))

    if current_user.status == 3:
        return redirect(url_for('teacher.dashboard'))

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


@home.route('/training_home')
@login_required
def training_home():
    client = current_user
    id_subjects = client.subjects.split(",")
    student_subjects = []
    for id_subject in id_subjects:
        new_subject = Subject.query.get_or_404(id_subject)
        new_subject_name = new_subject.subject
        student_subjects.append(new_subject_name)

    return render_template('home/train/training_home.html', student_subjects=student_subjects,
                           id_subjects=id_subjects, title="Тренировка")


@home.route('/training_subject/<int:subject_id>')
@login_required
def training_subject(subject_id):
    return render_template('home/train/training_subject.html', subject_id = subject_id, title="Тренировка")


@home.route('/ege')
@login_required
def ege():
    return render_template('home/train/ege.html', title="Вариант ЕГЭ")


@home.route('/ege/send_error/<int:task_id>', methods=['GET', 'POST'])
@login_required
def send_error(task_id):
    error = TasksError(task_id=task_id, error=request.form['text'])
    db.session.add(error)
    db.session.commit()


@home.route('/recommendation_question')
@login_required
def recommendation_question():
    return render_template('home/train/recommendation_question.html', title="Рекомендуем отработать")


@home.route('/recommendation_answer')
@login_required
def recommendation_answer():
    return render_template('home/train/recommendation_answer.html', title="Рекомендуем отработать")


@home.route('/choice')
@login_required
def choice():
    return render_template('home/train/choice.html', title="Выбор задания")


@home.route('/answers_ege')
@login_required
def answers_ege():
    return render_template('home/train/answers_ege.html', title="Решения и ответы")


@home.route('/results')
@login_required
def results():
    return render_template('home/train/results.html', title="Результаты")


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


@home.route('/road_map', methods=['GET', 'POST'])
@login_required
def road_map():
    road_map_items = RoadMap.query.filter(RoadMap.client_id == current_user.id).order_by(
        RoadMap.step.asc()).all()
    return render_template('home/road_map.html', road_map_items=road_map_items, title='Дорожная карта')


@home.route('/chat-bot', methods=['GET', 'POST'])
@login_required
def chat_bot():
    return render_template('home/chat-bot.html', title='Чат-бот')


@home.route('/set_time', methods=['GET', 'POST'])
@login_required
def set_time():
    return render_template('home/set_time.html', title='Указать расписание')


@home.route('/materials_home')
@login_required
def materials_home():
    return render_template('home/materials_home.html', title='Материалы')


@home.route('/material')
@login_required
def material():
    return render_template('home/material.html', title='Материал')


@home.route('/training/<inLid>/start_rec')
@login_required
def start_rec(id):
    n_que_subj = TrainingChoice.query.get_or_404(TrainingChoice.subject == id).number
    weights = []
    const = 0.1
    for i in range(1, n_que_subj):
        right_answ = 0
        answers = Answer.query.filter(
            (Answer.subject_id == id) & (Answer.client_id == current_user.id) & (Answer.task_num == i)).all()
        for answer in answers:
            right_answ += answer.right
        if len(answers) != 0:
            probability = 1 - (right_answ / len(answers))
        else:
            probability = 0
        weights.append(probability + const)

    n_questions = 10
    questions_num = choice(range(1, n_que_subj), n_questions, p=weights)
    questions_list = []
    for question_num in questions_num:
        question = Task.query.filter(Task.number == question_num).all()
        questions_list.append(random.choice(question).id)
    train_session = TrainingRecommendationSession(client_id=current_user.id, subject_id=id,
                                                  start_date=datetime.datetime.now(), qustions=questions_list,
                                                  current_question=1)
    db.session.add(train_session)
    db.session.commit()
    return redirect()
