from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class SubjectEditForm(FlaskForm):
    subject = StringField('Название предмета', validators=[DataRequired()])
    description = TextAreaField('Описание предмета', validators=[DataRequired()])
    submit = SubmitField('Изменить')

class SubjectAddForm(FlaskForm):
    subject = StringField('Название предмета', validators=[DataRequired()])
    description = TextAreaField('Описание предмета', validators=[DataRequired()])
    submit = SubmitField('Создать')