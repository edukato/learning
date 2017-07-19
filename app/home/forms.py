from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class AccountEditForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    photo = FileField('Ваша фотограия', validators=[FileAllowed(['jpg', 'png'], 'Изображения только!')])
    submit = SubmitField('Изменить')
