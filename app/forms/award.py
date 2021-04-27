from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired


class AwardForm(FlaskForm):
    """Форма для добавления и редактирования награды
    (для редактирования будут подставлятся данные в форму, кроме файла картинки)
    """
    title = StringField('Заголовок', validators=[DataRequired()])
    direction = StringField('Направление награды', validators=[DataRequired()])
    description = TextAreaField("Описание награды", validators=[DataRequired()])
    file_field = FileField("Картинка награды")
    submit = SubmitField('Сохранить')
