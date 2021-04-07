from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from flask_wtf.html5 import EmailField
from wtforms.validators import DataRequired


class AdminLoginForm(FlaskForm):
    """Форма входа в аккаунт для админа"""
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AdminRegisterForm(FlaskForm):
    """Форма для регистрации аккаунта админа (доступно только в debug)"""
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    submit = SubmitField('Войти')
