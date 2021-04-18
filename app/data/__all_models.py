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


class Award(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'awards'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, default="Достижение")
    # Имя файла изображения награды
    image_filename = sqlalchemy.Column(sqlalchemy.String, default="", nullable=True)
    direction = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class Category(SqlAlchemyBase, SerializerMixin):
    """Модель категории для новостей на сайте"""

    __tablename__ = 'categories'

    association_table = sqlalchemy.Table(
        'association',
        SqlAlchemyBase.metadata,
        sqlalchemy.Column('news', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('news.id')),
        sqlalchemy.Column('category', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('categories.id'))
    )

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class News(SqlAlchemyBase, SerializerMixin):
    """Модель новости"""

    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    categories = sqlalchemy.orm.relation("Category",
                                         secondary="association",
                                         backref="news")
    creation_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())