# app/home/views.py

import datetime, os, random

import vk
from . import messageHandler

from numpy import random

from flask import flash, redirect, render_template, url_for, abort, request, json
from flask_login import login_required, current_user
from .settings import *

from werkzeug.utils import secure_filename

from . import home
from ..models import Service, SellingLog, Client, RoadMap, TasksError, TrainingRecommendationSession, Answer, \
    TrainingChoice, Task, Subject, TrainingChoice, Schedule, Teacher, MentorsClaim, Skil, Material, OperatingSchedules
from .. import db
from .forms import AccountEditForm
from ..utils import awesome_date


def check_student():
    if current_user.status != 1:
        abort(403)


@home.route('/')
def homepage():
    if current_user.is_authenticated:
        if current_user.status == 1:
            return redirect(url_for('home.account'))
        else:
            if current_user.status == 2:
                return redirect(url_for('admin.dashboard'))
            else:
                if current_user.status == 3:
                    return redirect(url_for('teacher.dashboard'))
    else:
        return render_template('home/index.html', title="Добро пожаловать в edukato!")

@home.route('/agreement')
def agreement():
        return render_template('home/agreement.html', title="Пользовательское соглашение!")


@home.route('/vk', methods=['POST'])
def vk_processing():
    data = json.loads(request.data)
    if 'type' not in data.keys():
        return 'not vk'
    if data['type'] == 'confirmation':
        return confirmation_token
    elif data['type'] == 'message_new':
        messageHandler.create_answer(data['object'], token)
        return 'ok'


@home.route('/parents')
def parents():
    return render_template('home/parents.html', title="Родителям!")
@home.route('/account')
@login_required
def account():
    check_student()

    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))

    if current_user.status == 2:
        return redirect(url_for('admin.dashboard'))

    if current_user.status == 3:
        return redirect(url_for('teacher.dashboard'))

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    schedule = Schedule.query.filter(
        (Schedule.client_id == current_user.id) & (Schedule.time >= datetime.datetime.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0))).all()

    for schedule_item in schedule:
        schedule_item.day = schedule_item.time.day
        schedule_item.subject_name = Subject.query.get_or_404(schedule_item.subject_id).subject
        schedule_item.dow = schedule_item.time.weekday()
        schedule_item.day_of_week = weekdays[schedule_item.dow]
        schedule_item.date = awesome_date(schedule_item.time)
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

    teacher = Teacher.query.filter(Teacher.id == current_user.mentor).first()
    mentor = None
    if not (teacher == None):
        mentor = Client.query.get_or_404(teacher.login_id)

    if current_user.plan:
        plan = SellingLog.query.get_or_404(current_user.plan)
    else:
        plan = None

    if plan != None:
        next_pay = awesome_date(plan.access_end)
    else:
        next_pay = ""

    next_material = Material.query.filter(Material.date > datetime.datetime.now()).first()
    if (next_material):
        next_material_date = awesome_date(next_material.date)
    else:
        next_material_date = "материал будет совсем скоро"

    return render_template('home/account.html', plan=plan, schedule=byweeks, weekdays=weekdays,
                           mentor=mentor, teacher=teacher, next_pay=next_pay,
                           next_material_date = next_material_date,
                           title="Мой аккаунт")


@home.route('/account/send_claim/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def account_send_claim(teacher_id):
    claim = MentorsClaim(client_id=current_user.id, teacher_id=teacher_id, claim=request.form['text'])
    db.session.add(claim)
    db.session.commit()


@home.route('/shop')
@login_required
def shop():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))

    sel_log = SellingLog.query.get_or_404(current_user.plan)

    return render_template('home/shop.html', sel_log = sel_log, title="Магазин")

@home.route('/block')
@login_required
def block():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))

    sel_log = SellingLog.query.filter(SellingLog.client_id == current_user.id).order_by(SellingLog.id.desc()).first()

    return render_template('home/block.html', sel_log = sel_log, title="Магазин")


@home.route('/pay')
@login_required
def pay():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    return render_template('home/pay.html', title="Пополнение счёта")


@home.route('/training_home')
@login_required
def training_home():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    client = current_user
    rec = True
    if (client.loboda_date != None):
        if ((client.loboda_date.replace(hour=0, minute=0, second=0, microsecond=0)) == (
                datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))):
            rec = True
        else:
            rec = False
    else:
        rec = False
    if client.subjects is not None:
        id_subjects = client.subjects.split(",")
    else:
        id_subjects = []
    student_subjects = []
    student_subjects_small = []
    for id_subject in id_subjects:
        new_subject = Subject.query.get_or_404(id_subject)
        new_subject_name = new_subject.subject
        student_subjects.append(new_subject_name)
        student_subjects_small.append(new_subject_name.lower())

    deltatime = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - client.date_of_reg.replace(
        hour=0, minute=0, second=0, microsecond=0)

    have_not_subjects = False
    rec_subject = 0

    if (len(student_subjects) != 0):
        rec_subject = (int(deltatime.days) % len(student_subjects)) + 1

    return render_template('home/train/training_home.html', student_subjects=student_subjects,
                           student_subjects_small=student_subjects_small,
                           id_subjects=id_subjects, rec_subject=rec_subject - 1, rec=rec,
                           have_not_subjects=have_not_subjects, title="Тренировка")


@home.route('/training_subject/<int:subject_id>')
@login_required
def training_subject(subject_id):
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    descriptions = []
    skils = Skil.query.filter(Skil.client_id == current_user.id).filter(Skil.subject == subject_id).all()
    training_choices = TrainingChoice.query.filter(TrainingChoice.subject_id == subject_id).all()
    for training_choice in training_choices:
        descriptions.append(training_choice.description)
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
                           id_subjects=id_subjects, skils=skils, descriptions=descriptions, title="Тренировка")


@home.route('/ege/<int:subject_id>/<int:training_type>', methods=['GET', 'POST'])
@login_required
def ege(subject_id, training_type):
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    number_of_tasks = Subject.query.get_or_404(subject_id).tasks_number
    if training_type == 0:
        final_tasks = []
        for i in range(number_of_tasks):
            tasks = Task.query.filter((Task.subject_id == subject_id) & (Task.number == (i + 1))).all()
            final_task = random.choice(tasks)
            final_tasks.append(final_task)

        return render_template('home/train/ege.html', tasks=final_tasks, subject_id=subject_id,
                               tasks_quantity=number_of_tasks, training_type=training_type, title="Вариант ЕГЭ")

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
            task = Task.query.filter(Task.number == int(question_num)).filter(Task.subject_id == subject_id).all()
            tasks.append(random.choice(task))

        return render_template('home/train/ege.html', tasks=tasks, subject_id=subject_id,
                               tasks_quantity=n_questions, training_type=training_type, title='Рекомендумые задания')

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
                               tasks_quantity=tasks_quantity, training_type=training_type, title="Вариант ЕГЭ")


@home.route('/ege/send_error/<int:task_id>', methods=['GET', 'POST'])
@login_required
def send_error(task_id):
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    error = TasksError(task_id=task_id, error=request.form['text'])
    db.session.add(error)
    db.session.commit()

@home.route('/choice/<int:subject_id>')
@login_required
def choice(subject_id):
    check_student()
    if current_user.step_number != 0: return redirect(url_for('home.step_' + str(current_user.step_number)))
    training_choices = TrainingChoice.query.filter(TrainingChoice.subject_id == subject_id).all()
    descriptions = []
    for training_choice in training_choices:
        descriptions.append(training_choice.description)

    return render_template('home/train/choice.html', subject_id=subject_id, descriptions=descriptions,
                           title="Выбор задания")


@home.route('/answers_ege/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def answers_ege(subject_id):
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    training_type = int(request.form['type_of_train'])
    if (training_type == 1):
        client = Client.query.get_or_404(current_user.id)
        client.loboda_date = datetime.datetime.now()
        db.session.commit()
    subject = Subject.query.get_or_404(subject_id)
    tasks = []
    task = Task
    number_of_tasks = int(request.form['number_of_tasks'])
    for i in range(number_of_tasks):
        task = Task.query.get_or_404(request.form['id_for_task_' + str(i + 1)])
        tasks.append(task)
    descriptions = []
    for i in range(subject.tasks_number):
        training_choice = TrainingChoice.query.filter(TrainingChoice.subject_id == subject_id).filter(
            TrainingChoice.number == (i + 1)).all()
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
                     subject_id=subject_id, task_number=tasks[i].number, training_type=training_type)
        db.session.add(ans)

    type_tasks = [[]]

    for i in range(subject.tasks_number):
        for a in range(number_of_tasks):
            if (tasks[a].number == (i + 1)):
                type_tasks[i].append(tasks[a])
        if (len(type_tasks) < subject.tasks_number):
            type_tasks.append([])

    right_answers_amount = 0
    answers_amount = 0
    c = 0
    change_up = False
    change_down = False
    levels_up = []
    levels_down = []
    old_skil_levels = []
    new_skil_levels = []
    show_skils = []
    show_skils_first_time = []
    for i in range(subject.tasks_number):
        b = 0
        answers_amount = len(Answer.query.filter(Answer.client_id == current_user.id).filter(
            Answer.subject_id == subject_id).filter(Answer.task_number == i + 1).all())
        if (answers_amount > 0):
            old_skil = (Skil.query.filter(Skil.client_id == current_user.id).filter(Skil.subject == subject_id).filter(
                Skil.number == (i + 1)).all())[0]
            old_percent = old_skil.right_percent

            new_right_answers_amount = 0
            new_answers_amount = 0
            for a in range(len(type_tasks[i])):
                new_right_answers_amount += results[c]
                new_answers_amount += 1
                c += 1
                b += 1
            right_answers_amount = (answers_amount - new_answers_amount) * old_percent
            new_right_percent = ((right_answers_amount + new_right_answers_amount) / (answers_amount))
            old_skil.right_percent = new_right_percent
            old_skil.answers_amount += b
            if (old_skil.answers_amount >= 5):
                if (old_skil.answers_amount == 5):
                    show_skils_first_time.append(True)
                else:
                    show_skils_first_time.append(False)
                show_skils.append(True)
                if (old_skil.answers_amount > 5):
                    old_skil_level = old_skil.level
                    old_skil_levels.append(old_skil_level)
                else:
                    old_skil_level = 0
                    old_skil_levels.append(old_skil_level)
                new_skil_level = int(((new_right_percent * 100) // (25)) + 1)
                if (new_skil_level == 5):
                    new_skil_level = 4
                new_skil_levels.append(new_skil_level)
                if (int(old_skil_level) > int(new_skil_level)):
                    levels_down.append(True)
                    levels_up.append(False)
                    change_down = True
                elif (int(new_skil_level) > int(old_skil_level)):
                    levels_down.append(False)
                    levels_up.append(True)
                    change_up = True
                else:
                    levels_down.append(False)
                    levels_up.append(False)
                old_skil.level = int(new_skil_level)
            else:
                show_skils.append(False)
            db.session.commit()


    return render_template('home/train/answers_ege.html', tasks=tasks, descriptions=descriptions, subject_id=subject_id,
                           number_of_tasks=number_of_tasks, results=results, answers=answers, levels_up=levels_up,
                           levels_down=levels_down, old_skil_levels=old_skil_levels,
                           new_skil_levels=new_skil_levels, show_skils=show_skils,
                           show_skils_first_time=show_skils_first_time, change_down=change_down, change_up=change_up,
                           title="Решения и ответы")


@home.route('/results/<int:subject_id>')
@login_required
def results(subject_id, tasks):
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
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
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    return render_template('home/help.html', title="Служба поддержки")


@home.route('/contacts')
@login_required
def contacts():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    return render_template('home/contacts.html', title="Контакты")


@home.route('/shop/confirm/<int:consult>/<int:lesson>/<int:typeof>', methods=['GET', 'POST'])
@login_required
def confirm_transaction(consult,lesson,typeof):
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))

    if typeof == 0:
        new_payment = SellingLog.query.filter((SellingLog.access_start >= datetime.datetime.now()) & (SellingLog.client_id == current_user.id)).all()
        if new_payment:
            return render_template('home/confirm_transaction.html', case = 0, title="Но ведь вы уже купили на следующий месяц")
        else:
            return redirect(url_for('home.confirmed_transaction', consult=consult, lesson=lesson, typeof=typeof))
    else:
        plan = SellingLog.query.get_or_404(current_user.plan)
        if ((plan.lessons > lesson) or (plan.consultations > consult)) or (plan.lessons == lesson and plan.consultations == consult):
            return render_template('home/confirm_transaction.html', case = 1, title="Выбрал меньше, чем есть")
        else:
            return redirect(url_for('home.confirmed_transaction', consult=consult, lesson=lesson, typeof=typeof))


@home.route('/shop/confirmed/<int:consult>/<int:lesson>/<int:typeof>', methods=['GET', 'POST'])
@login_required
def confirmed_transaction(consult,lesson,typeof):
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))

    if consult == 0:
        price_cons = 0
    else:
        if consult == 1:
            price_cons = 400
        else:
            if consult == 2:
                price_cons = 350
            else:
                if consult == 3:
                    price_cons = 325
                else:
                    if consult > 3 :
                        price_cons = 300

    if lesson == 0:
        price_less = 0
    else:
        if lesson == 1:
            price_less = 600
        else:
            if lesson == 2:
                price_less = 550
            else:
                if lesson == 3:
                    price_less = 525
                else:
                    if lesson > 3 :
                        price_less = 500

    price0 = price_less*lesson + price_cons*consult - 1
    price1 = price0 - SellingLog.query.get_or_404(current_user.plan).price


    if typeof == 0:
        if current_user.balance >= price0:
            sellogitem = SellingLog(access_start = SellingLog.query.get_or_404(current_user.plan).access_end, access_end = SellingLog.query.get_or_404(current_user.plan).access_end + datetime.timedelta(days = 30), client_id = current_user.id, lessons = lesson, consultations = consult, date_time = datetime.datetime.now(), price = price0)
            client = Client.query.get_or_404(current_user.id)
            client.balance -= price0
            db.session.add(sellogitem)
            db.session.commit()
            flash('Успешно')
            return redirect(url_for('home.shop'))

        else:
            flash('Нет денег')
            return redirect(url_for('home.shop'))
    else:
        if current_user.balance >= price1:
            sellogitem = SellingLog.query.get_or_404(current_user.plan)

            sellogitem.lessons_now += lesson - sellogitem.lessons
            sellogitem.consultations_now += consult - sellogitem.consultations

            sellogitem.consultations = consult
            sellogitem.lessons = lesson

            sellogitem.price = price0
            client = Client.query.get_or_404(current_user.id)
            client.balance -= price1
            db.session.commit()
            flash('Успешно')
            return redirect(url_for('home.shop'))
        else:
            flash('Нет денег')
            return redirect(url_for('home.shop'))



@home.route('/shop/show/<int:id>', methods=['GET', 'POST'])
@login_required
def show_service(id):
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    service = Service.query.get_or_404(id)

    review_list = []

    if service.reviews:
        reviews = service.reviews.split('(secret-splitter)')

        for review in reviews:
            review_list.append(review.split('(secret-splitter-1)'))

    return render_template('home/service.html',
                           service=service, review_list=review_list, title="Показать услугу")


@home.route('/account/edit', methods=['GET', 'POST'])
@login_required
def edit_account():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    client = Client.query.get_or_404(current_user.id)

    form = AccountEditForm(obj=client)
    if form.validate_on_submit():
        client.first_name = form.first_name.data
        client.last_name = form.last_name.data
        client.password = form.password.data
        if form.photo.data is not None:
            form.photo.data.save(
                'app/static/images/profile/' + str(current_user.id) + secure_filename(form.photo.data.filename))
            client.image = str(current_user.id) + secure_filename(form.photo.data.filename)
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
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    alltransactions = SellingLog.query.filter(SellingLog.client_id == current_user.id).all()
    for transaction in alltransactions:
        transaction.name = (Service.query.filter(Service.id == transaction.service_id).first()).name
    return render_template('home/transactions.html', transactions=alltransactions, title='Транзакции')


@home.route('/road_map', methods=['GET', 'POST'])
@login_required
def road_map():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    road_map_items = RoadMap.query.filter(RoadMap.client_id == current_user.id).order_by(
        RoadMap.step.asc()).all()
    return render_template('home/road_map.html', road_map_items=road_map_items, title='Дорожная карта')


@home.route('/chat-bot', methods=['GET', 'POST'])
@login_required
def chat_bot():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    return render_template('home/chat-bot.html', title='Чат-бот')


@home.route('/chat-bot/update', methods=['POST'])
@login_required
def chat_bot_upd():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    client = Client.query.get_or_404(current_user.id)
    if request.form.get('social'):
        client.social_network = request.form['social']
    if request.form.get('1'):
        client.chat_bot_1 = True
    if request.form.get('2'):
        client.chat_bot_2 = True
    if request.form.get('3'):
        client.chat_bot_3 = True
    if request.form.get('4'):
        client.chat_bot_4 = True
    if request.form.get('5'):
        client.chat_bot_5 = True
    db.session.commit()
    return redirect(url_for('home.chat_bot'))


@home.route('/set_time', methods=['GET', 'POST'])
@login_required
def set_time():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    return render_template('home/set_time.html', title='Указать расписание')


@home.route('/materials/home')
@login_required
def materials_home():
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    if current_user.subjects is not None:
        id_subjects = current_user.subjects.split(",")
    else:
        id_subjects = []
    student_subjects = []
    for id_subject in id_subjects:
        new_subject = Subject.query.get_or_404(id_subject)
        new_subject_name = new_subject.subject
        student_subjects.append([id_subject, new_subject_name])

    materials = Material.query.filter(Material.date <= datetime.datetime.now()).all()

    for material in materials:
        key = False
        for id_subject in id_subjects:
            if int(material.subject_id) == int(id_subject):
                key = True
        if not key:
            materials.remove(material)

    print(materials)
    for material in materials:
        teacher = Client.query.get_or_404(Teacher.query.get_or_404(material.teacher_id).login_id)
        material.teacher_name = teacher.first_name + ' ' + teacher.last_name
        material.teacher_descript = teacher.description
        material.teacher_image = teacher.image
        material.date_t = awesome_date(material.date)

    return render_template('home/materials_home.html', materials=materials, subjects=student_subjects,
                           title='Материалы')


@home.route('/materials/<int:id>')
@login_required
def materials_subj(id):
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    subject = Subject.query.get_or_404(id).subject

    if current_user.subjects is not None:
        id_subjects = current_user.subjects.split(",")
    else:
        id_subjects = []

    key = False

    for id_subject in id_subjects:
        if int(id) == int(id_subject):
            key = True
    if not key:
        abort(403)

    materials = Material.query.filter((Material.date <= datetime.datetime.now()) & (Material.subject_id == id)).all()

    for material in materials:
        teacher = Client.query.get_or_404(Teacher.query.get_or_404(material.teacher_id).login_id)
        material.teacher_name = teacher.first_name + ' ' + teacher.last_name
        material.teacher_descript = teacher.description
        material.teacher_image = teacher.image
        material.date_t = awesome_date(material.date)

    return render_template('home/materials_subject.html', materials=materials, subject=subject,
                           title='Материалы')


@home.route('/material/<int:id>')
@login_required
def material(id):
    check_student()
    if current_user.step_number != 0:
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    material = Material.query.get_or_404(id)
    if current_user.subjects is not None:
        id_subjects = current_user.subjects.split(",")
    else:
        id_subjects = []

    key = False

    for id_subject in id_subjects:
        if int(id_subject) == int(material.subject_id):
            key = True

    if not key:
        abort(403)

    material.date_t = awesome_date(material.date)
    teacher = Client.query.get_or_404(Teacher.query.get_or_404(material.teacher_id).login_id)
    material.teacher_name = teacher.first_name + ' ' + teacher.last_name
    material.teacher_descript = teacher.description
    material.teacher_image = teacher.image
    return render_template('home/material.html', material=material, title='Материал')

@home.route('/step/0')
@login_required
def step_0():
    return redirect(url_for('home.account'))

@home.route('/step/1')
@login_required
def step_1():
    if (int(current_user.step_number) != 1) or (not current_user.step_number):
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))

    return render_template('home/wizard/step_1.html')


@home.route('/step/2/<int:year>', methods=['GET', 'POST'])
@login_required
def step_2(year):

    current_user.year_of_study = year
    db.session.commit()

    if current_user.step_number == 1 or current_user.step_number == 2:
        current_user.step_number = 2
        current_user.year_of_study = year
        db.session.commit()
        return render_template('home/wizard/step_2.html')
    else:
        return redirect(url_for('home.step_' + str(current_user.step_number)))


@home.route('/step/3', methods=['GET', 'POST'])
@login_required
def step_3():
    if current_user.step_number != 3:
        try:
            univ = request.form['university']
            if univ == "":
                redirect(url_for('step_2', year = current_user.year_of_study))
            current_user.wish_list = univ
            current_user.step_number = 3
            db.session.commit()
        except:
            if current_user.step_number != 2:
                return redirect(url_for('home.step_' + str(current_user.step_number)))
            else:
                return redirect(url_for('home.step_2', year = current_user.year_of_study))

    subjects = Subject.query.filter(Subject.id != 9).all()

    return render_template('home/wizard/step_3.html', subjects=subjects)


@home.route('/step/4', methods=['GET','POST'])
@login_required
def step_4():
    all_subjects = Subject.query.all()
    wish_subjects = []
    wish_subjects_string = ""
    separator = ','

    if current_user.step_number != 4:
        for subject in all_subjects:
            if request.form.get(str(subject.id)):
                wish_subjects.append(str(subject.id))

        if len(wish_subjects) == 0:
            if current_user.step_number == 3:
                flash("Необходимо выбрать хотя бы один предмет")
            if current_user.step_number != 2:
                return redirect(url_for('home.step_' + str(current_user.step_number)))
            else:
                return redirect(url_for('home.step_2', year = current_user.year_of_study))

    current_user.step_number = 4
    if not current_user.interesting_subjects:
        wish_subjects_string = separator.join(wish_subjects)
        current_user.interesting_subjects = wish_subjects_string
    db.session.commit()

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    opschedule = OperatingSchedules.query.all()

    now = datetime.datetime.now()
    endweek = now + datetime.timedelta(days=(7 - now.weekday()))
    endweek = endweek.replace(hour=0, minute=0, second=0, microsecond=0)

    byweeks = list()
    for i in range(3):
        week = [[], [], [], [], [], [], []]
        for opschedule_item in opschedule:
            opschedule_item.subject_name = Subject.query.get_or_404(opschedule_item.subject_id).subject
            opsch_teacher_id = Teacher.query.get_or_404(opschedule_item.teacher_id).login_id
            opsch_teacher = Client.query.get_or_404(opsch_teacher_id)
            opschedule_item.teacher_name = opsch_teacher.last_name + ' ' + opsch_teacher.first_name + ' ' + opsch_teacher.middle
            week[opschedule_item.day_of_the_week].append(opschedule_item)
            opschedule_item.time_start_temp = datetime.timedelta(minutes=opschedule_item.interval_number*30)
            opschedule_item.time_end_temp = opschedule_item.time_start_temp + datetime.timedelta(minutes=30)
            opschedule_item.time_start = datetime.time(opschedule_item.time_start_temp.seconds // 3600, (opschedule_item.time_start_temp.seconds % 3600)//60, 0).strftime("%H:%M")
            opschedule_item.time_end = datetime.time(opschedule_item.time_end_temp.seconds // 3600, (opschedule_item.time_end_temp.seconds % 3600)//60, 0).strftime("%H:%M")
        byweeks.append(week)

    for i in range(0, now.weekday()):
        byweeks[0][i] = [][:]

    now_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    day_counter = 0

    for week in byweeks:
        print(week)
        for day in week:
            day_counter += 1
            print(day)
            for schedule_item in day:
                if Schedule.query.filter((Schedule.time == (
                    now_day + datetime.timedelta(days=day_counter - now_day.weekday() - 1))) & (
                            Schedule.interval_number == schedule_item.interval_number)).all():
                    print('kek')
                    day.remove(schedule_item)

    return render_template('home/wizard/step_4.html', weekdays=weekdays, byweeks=byweeks)


@home.route('/addition/<int:week>/<int:id>')
@login_required
def schedule_addition(week, id):
    check_student()

    now_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    op_schedule = OperatingSchedules.query.get_or_404(id)
    schedule_item = Schedule(client_id=current_user.id, teacher_id=op_schedule.teacher_id,
                             time=(now_day + datetime.timedelta(
                                 days=(week * 7 - now_day.weekday() + op_schedule.day_of_the_week))),
                             interval_number=op_schedule.interval_number, subject_id = 9)
    db.session.add(schedule_item)

    client = Client.query.get_or_404(current_user.id)
    client.step_number = 5
    client.mentor = op_schedule.teacher_id
    db.session.commit()

    return redirect(url_for('home.step_5'))


@home.route('/step/5')
@login_required
def step_5():
    if current_user.step_number != 5 or (not current_user.step_number):
        if current_user.step_number != 2:
            return redirect(url_for('home.step_' + str(current_user.step_number)))
        else:
            return redirect(url_for('home.step_2', year = current_user.year_of_study))
    mentor = Client.query.get_or_404(Teacher.query.get_or_404(current_user.mentor).login_id)
    mentor.skype = Teacher.query.get_or_404(current_user.mentor).skype_login
    consult = Schedule.query.filter(
        (Schedule.client_id == current_user.id) & (Schedule.teacher_id == current_user.mentor)).first()
    consult.date = awesome_date(consult.time)
    return render_template('home/wizard/step_5.html', consult=consult, mentor=mentor)
