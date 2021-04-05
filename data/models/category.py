from data.db_session import SqlAlchemyBase

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin


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
