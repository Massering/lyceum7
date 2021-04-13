from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from flask_wtf.html5 import EmailField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    """Форма для добавления и редактирования новости
    (для редактирования будут подставлятся данные в форму)"""
    title = StringField('Заголовок', validators=[DataRequired()])
    description = TextAreaField('Содержание', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
