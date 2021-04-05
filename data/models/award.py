from data.db_session import SqlAlchemyBase

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin


class Award(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'awards'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, default="Достижение")
    # Имя файла изображения награды
    image_filename = sqlalchemy.Column(sqlalchemy.String, default="", nullable=True)
    direction = sqlalchemy.Column(sqlalchemy.String, nullable=False)
