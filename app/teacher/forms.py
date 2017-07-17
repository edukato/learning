from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired


class MaterialEditForm(FlaskForm):
    subject = StringField('Название предмета', validators=[DataRequired()])
    description = TextAreaField('Описание предмета', validators=[DataRequired()])
    text = TextAreaField('Текст', validators=[DataRequired()])
    submit = SubmitField('Изменить')