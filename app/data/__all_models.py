import datetime

from .db_session import SqlAlchemyBase

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Admin(SqlAlchemyBase, SerializerMixin, UserMixin):
    """Модель админа, который будет добавлять новости, достижения и
    прочий не статичный контент"""

    __tablename__ = 'admins'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def set_password(self, password: str):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.hashed_password, password)


class News(SqlAlchemyBase, SerializerMixin):
    """Модель новости"""

    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True, nullable=False, index=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    content = sqlalchemy.Column(sqlalchemy.String)
    # Пути к изображениям новости, через запятую
    paths_to_images = sqlalchemy.Column(sqlalchemy.String, default="")
    creation_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())


class Award(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'awards'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True, nullable=False, index=True)
    title = sqlalchemy.Column(sqlalchemy.String, default="Достижение")
    # Имя файла изображения награды
    image_filename = sqlalchemy.Column(sqlalchemy.String, default="")
    direction = sqlalchemy.Column(sqlalchemy.String, default="")
    description = sqlalchemy.Column(sqlalchemy.String, default="")
    creation_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
