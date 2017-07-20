from flask_wtf import FlaskForm
import datetime
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.fields.html5 import DateTimeField
from wtforms.validators import DataRequired


class SubjectEditForm(FlaskForm):
    subject = StringField('Название предмета', validators=[DataRequired()])
    description = TextAreaField('Описание предмета', validators=[DataRequired()])
    submit = SubmitField('Изменить')


class SubjectAddForm(FlaskForm):
    subject = StringField('Название предмета', validators=[DataRequired()])
    description = TextAreaField('Описание предмета', validators=[DataRequired()])
    submit = SubmitField('Создать')


class ChoiceAddForm(FlaskForm):
    number = IntegerField('Номер задания', validators=[DataRequired()])
    description = StringField('Описание задания', validators=[DataRequired()])
    submit = SubmitField('Создать')


class ChoiceEditForm(FlaskForm):
    description = StringField('Описание задания', validators=[DataRequired()])
    submit = SubmitField('Изменить')


class TaskAddForm(FlaskForm):
    number = IntegerField('Номер задания', validators=[DataRequired()])
    question = TextAreaField('Вопрос', validators=[DataRequired()])
    answer = StringField('Ответ', validators=[DataRequired()])
    solution = TextAreaField('Решение', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class SalaryForm(FlaskForm):
    amount = IntegerField('Сумма, ₽', validators=[DataRequired()])
    description = TextAreaField('Описание')
    submit = SubmitField('Готово')


class AddMaterial(FlaskForm):
    first_name = TextAreaField('Имя', validators=[DataRequired()])
    last_name = TextAreaField('Фамилия', validators=[DataRequired()])
    subject = TextAreaField('Предмет', validators=[DataRequired()])
    date = DateTimeField('Дата и время выхода', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    submit = SubmitField('Готово')
