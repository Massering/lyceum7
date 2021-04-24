from .news_parser import parse_args

from data import db_session
from data.__all_models import News

from flask import jsonify
from flask_restful import Resource, abort
from sqlalchemy.exc import InvalidRequestError, IntegrityError


def get_news_by_id(news_id: int):
    """
    Функция возвращает новость по id, или
    вызывает HTTPException по коду 404
    """
    session = db_session.create_session()
    result = session.query(News).get(news_id)
    if result is None:
        abort(404)
        return
    return result


class NewsResource(Resource):
    """Класс представляющий ресурс одной новости News"""

    # Сообщения об ошибках:
    NEWS_ALREADY_DELETED = "News with id: '{0}' has already deleted"

    def get(self, news_id: int):
        news = get_news_by_id(news_id)
        return jsonify({"success": True, "news": news.to_dict(
            only=("id", "title", "content",
                  "creation_time", "modified_date"))})

    def delete(self, news_id: int):
        news = get_news_by_id(news_id)
        session = db_session.create_session()
        try:
            session.delete(news)
            session.commit()
        # FIXME: is comment below correct?
        # Обработка случая, если такая новость уже удалена
        except InvalidRequestError as e:
            return jsonify({"success": False, "error": self.NEWS_ALREADY_DELETED})

        return jsonify({"success": True})

    def put(self):
        args = parse_args()
        # Получение новости и переопределение параметров
        news = get_news_by_id(args["id"])
        news.title = args["title"]
        news.content = args["content"]
        news.creation_time = args["creation_time"]
        news.modified_date = args["modified_date"]
        # TODO: тут точно ничего не упадёт?
        session.commit()
        return jsonify({"success": True})


class NewsListResource(Resource):
    """Класс представляющий ресурс нескольких новостей"""

    # Сообщения об ошибках:
    NEWS_ALREADY_EXISTS = "News with id: '{0}' is already exists"

    def get(self):
        session = db_session.create_session()
        list_of_news = session.query(News).all()
        return jsonify({"success": True, "news_list": [news_item.to_dict(
            only=("id", "title", "content",
                  "creation_time", "modified_date")) for news_item in list_of_news]})

    def post(self):
        args = parse_args()
        session = db_session.create_session()
        news = News(
            id=args["id"],
            title=args["title"],
            content=args["content"],
            creation_time=args["creation_time"],
            modified_date=args["modified_date"],
        )
        try:
            session.add(news)
            session.commit()
        # Обработка случая, если такая новость уже существует
        except IntegrityError as e:
            session.rollback()
            return jsonify({"success": False,
                            "error": self.NEWS_ALREADY_EXISTS.format(args['id'])
                            })
        return jsonify({"success": True})
