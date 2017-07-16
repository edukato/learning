# app/home/views.py

import datetime, os, random

from numpy import random

from flask import flash, redirect, render_template, url_for, abort, request
from flask_login import login_required, current_user

from . import home
from ..models import Service, SellingLog, Client, RoadMap, TasksError, TrainingRecommendationSession, Answer, \
    TrainingChoice, Task, Subject, TrainingChoice, Schedule, Teacher
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

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    schedule = Schedule.query.filter(
        (Schedule.client_id == current_user.id) & (Schedule.time > datetime.datetime.now())).all()

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

    return render_template('home/account.html', schedule=byweeks, weekdays=weekdays, active_services=active_services,
                           title="Мой аккаунт")


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
    if client.subjects is not None:
        id_subjects = client.subjects.split(",")
    else:
        id_subjects = []
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
    client = current_user
    if client.subjects is not None:
        id_subjects = client.subjects.split(",")
    else:
        id_subjects = []
    student_subjects = []
    for id_subject in id_subjects:
        new_subject = Subject.query.get_or_404(id_subject)
        new_subject_name = new_subject.subject
        student_subjects.append(new_subject_name)
    return render_template('home/train/training_subject.html', subject_id=subject_id, student_subjects=student_subjects,
                           id_subjects=id_subjects, title="Тренировка")


@home.route('/ege/<int:subject_id>/<int:training_type>', methods=['GET', 'POST'])
@login_required
def ege(subject_id, training_type):
    number_of_tasks = Subject.query.get_or_404(subject_id).tasks_number
    if training_type == 0:
        final_tasks = []
        for i in range(number_of_tasks):
            tasks = Task.query.filter((Task.subject_id == subject_id) & (Task.number == (i + 1))).all()
            final_task = random.choice(tasks)
            final_tasks.append(final_task)

        return render_template('home/train/ege.html', tasks=final_tasks, subject_id=subject_id,
                               tasks_quantity=number_of_tasks, title="Вариант ЕГЭ")

    if training_type == 1:
        tasks = []
        weights = []
        const = 0.4
        for i in range(number_of_tasks):
            right_answ = 0
            answers = Answer.query.filter(
                (Answer.subject_id == subject_id) & (Answer.client_id == current_user.id) & (
                    Answer.task_number == (i + 1))).all()
            for answer in answers:
                right_answ += answer.right
            if len(answers) != 0:
                probability = 1 - (right_answ / len(answers))
            else:
                probability = 0
            weights.append(probability + const)

        weights_summ = 0
        for weight in weights:
            weights_summ += weight
        for i in range(len(weights)):
            weights[i] = weights[i] / weights_summ
        n_questions = 5
        questions_num = random.choice(range(1, number_of_tasks + 1), n_questions, p=weights)
        for question_num in questions_num:
            task = Task.query.filter(Task.number == int(question_num)).all()
            tasks.append(random.choice(task))

        return render_template('home/train/ege.html', tasks=tasks, subject_id=subject_id,
                               tasks_quantity=n_questions, title='Рекомендумые задания')

    if training_type == 2:
        tasks = []
        tasks_quantity = 0
        for i in range(number_of_tasks):
            tasks.append(int(request.form[str(i + 1)]))
            tasks_quantity += int(request.form[str(i + 1)])

        final_tasks = []
        task_type_counter = 0
        for task_type in tasks:
            task_type_counter += 1
            _tasks = Task.query.filter((Task.subject_id == subject_id) & (Task.number == task_type_counter)).all()
            for i in range(task_type):
                final_task = random.choice(_tasks)
                final_tasks.append(final_task)
                _tasks.remove(final_task)
        return render_template('home/train/ege.html', tasks=final_tasks, subject_id=subject_id,
                               tasks_quantity=tasks_quantity, title="Вариант ЕГЭ")


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


@home.route('/choice/<int:subject_id>')
@login_required
def choice(subject_id):
    training_choices = TrainingChoice.query.filter(TrainingChoice.subject_id == subject_id).all()
    descriptions = []
    for training_choice in training_choices:
        descriptions.append(training_choice.description)

    return render_template('home/train/choice.html', subject_id=subject_id, descriptions=descriptions,
                           title="Выбор задания")


@home.route('/answers_ege/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def answers_ege(subject_id):
    tasks = []
    task = Task
    number_of_tasks = int(request.form['number_of_tasks'])
    for i in range(number_of_tasks):
        task = Task.query.get_or_404(request.form['id_for_task_' + str(i + 1)])
        tasks.append(task)
    descriptions = []
    for i in range(number_of_tasks):
        training_choice = TrainingChoice.query.filter(TrainingChoice.subject_id == subject_id).filter(
            TrainingChoice.number == tasks[i].number).all()
        description = training_choice[0].description
        descriptions.append(description)
    answers = []
    results = []
    for i in range(number_of_tasks):
        answer = request.form['answer_' + str(i + 1)]
        answers.append(answer)
        if answer == tasks[i].right_answer:
            results.append(True)
        else:
            results.append(False)

    for i in range(number_of_tasks):
        ans = Answer(client_id=current_user.id, task_id=tasks[i].id, answer=answers[i], right=results[i],
                     subject_id=subject_id, task_number=tasks[i].number)
        db.session.add(ans)
    db.session.commit()
    return render_template('home/train/answers_ege.html', tasks=tasks, descriptions=descriptions, subject_id=subject_id,
                           number_of_tasks=number_of_tasks, results=results, answers=answers, title="Решения и ответы")


@home.route('/results/<int:subject_id>')
@login_required
def results(subject_id, tasks):
    result = []
    for task in tasks:
        if (task.right_answer == request.form[('answer_' + str(task.id))]):
            task.append(True)
        else:
            task.append(False)

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
