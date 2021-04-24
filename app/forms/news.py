from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    """Форма для добавления и редактирования новости
    (для редактирования будут подставлятся данные в форму)"""
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    files_field = MultipleFileField("Картинки к новости", _name="images", validators=[])
    submit = SubmitField('Сохранить')
