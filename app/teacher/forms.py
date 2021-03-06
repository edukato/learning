from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired


class MaterialEditForm(FlaskForm):
    title = StringField('Название материала', validators=[DataRequired()])
    description = TextAreaField('Описание материала', validators=[DataRequired()])
    text = TextAreaField('Текст', validators=[DataRequired()])
    submit = SubmitField('Изменить')