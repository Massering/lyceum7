import datetime

from data.db_session import SqlAlchemyBase

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin


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
