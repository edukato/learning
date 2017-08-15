from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from ..models import Client

class RegistrationForm(FlaskForm):
    """
    Form for users to create new account
    """
    email = StringField('Электронная почта', validators=[DataRequired(), Email(message='Неверный email')])
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    middle = StringField('Отчество', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[
        DataRequired(),
        EqualTo('confirm_password', message='Пароли должны совпадать')
    ])
    confirm_password = PasswordField('Подтверждение пароля')
    submit = SubmitField('Зарегистрировать')

    def validate_email(self, field):
        if Client.query.filter_by(email=field.data).first():
            raise ValidationError('Данная электронная почта уже зарегистрированна')


class LoginForm(FlaskForm):
    """
    Form for users to login
    """
    email = StringField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Вход')
