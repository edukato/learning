from flask import flash, redirect, render_template, url_for, abort
from flask_login import login_required, current_user

from . import admin
from ..models import Client, Subject, TrainingChoice
from .. import db
from .forms import SubjectEditForm, SubjectAddForm


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
    students = Client.query.filter(Client.status == 1).all()
    teachers = Client.query.filter(Client.status == 3).all()
    return render_template('admin/clients.html', students=students, teachers=teachers, title='Клиенты')


@admin.route('/admin/subjects')
@login_required
def subjects():
    check_admin()
    list_subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=list_subjects, title='Клиенты')


@admin.route('/admin/subject/<int:id>', methods=['GET', 'POST'])
@login_required
def subject(id):
    check_admin()
    subject = Subject.query.get_or_404(id)

    choices = TrainingChoice.query.filter(TrainingChoice.subject_id)
    return render_template('admin/subject.html', subject=subject, title=subject.subject)


@admin.route('/admin/subject/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def subject_edit(id):
    check_admin()

    subject = Subject.query.get_or_404(id)
    form = SubjectEditForm(obj=subject)
    if form.validate_on_submit():
        subject.subject = form.subject.data
        subject.description = form.description.data
        flash('Изменения внесены')
        db.session.commit()
        return redirect(url_for('admin.subject', id=id))

    form.subject.data = subject.subject
    form.description.data = subject.description

    return render_template('admin/subject_edit.html', form=form, subject=subject, title=subject.subject)


@admin.route('/admin/subject/add', methods=['GET', 'POST'])
@login_required
def subject_add():
    check_admin()

    form = SubjectAddForm()
    if form.validate_on_submit():
        subject = Subject(subject=form.subject.data,
                          description=form.description.data)
        try:
            # add department to the database
            db.session.add(subject)
            db.session.commit()
            flash('Вы успешно добавили предмет.')
        except:
            # in case department name already exists
            flash('Ошибка: предмет существует.')
        return redirect(url_for('admin.subjects'))

    return render_template('admin/subject_add.html', form=form, title='Добавить предмет')
