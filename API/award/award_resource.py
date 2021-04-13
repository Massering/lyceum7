from award_parser import parse_args

from data import db_session
from data.__all_models.award import Award

from flask import jsonify
from flask_restful import Resource
from sqlalchemy.exc import InvalidRequestError, IntegrityError


def get_award_by_id(award_id: int):
    """
    Функция возвращает достижение по id, или
    None если достижение не найдено.
    """
    session = db_session.create_session()
    return session.query(Award).get(award_id)


class AwardResource(Resource):
    """Класс представляющий ресурс одного достижения Award"""

    # Сообщения об ошибках:
    AWARD_NOT_FOUND = "Award with id: '{0}' is not exists"
    AWARD_ALREADY_DELETED = "Award with id: '{0}' has already deleted"

    def get(self, award_id: int):
        award = get_award_by_id(award_id)
        if award is None:
            return jsonify({
                "success": False,
                "error": self.AWARD_NOT_FOUND.format(award_id)
            })
        return jsonify({"success": True, "news": award.to_dict(
            only=("id", "title", "content", "categories",
                  "creation_time", "modified_date"))})

    def delete(self, award_id: int):
        award = get_award_by_id(award_id)
        if award is None:
            return jsonify({
                "success": False,
                "error": self.AWARD_NOT_FOUND.format(award_id)
            })

        session = db_session.create_session()
        try:
            session.delete(award)
            session.commit()
        # Обработка случая, если такая награда уже удалена
        except InvalidRequestError as e:
            return jsonify({"success": False, "error": self.AWARD_ALREADY_DELETED})

        return jsonify({"success": True})


class AwardsListResource(Resource):
    """Класс представляющий ресурс нескольких наград"""

    # Сообщения об ошибках:
    AWARD_ALREADY_EXISTS = "News with id: '{0}' is already exists"

    def get(self):
        session = db_session.create_session()
        list_of_news = session.query(Award).all()
        return jsonify({"success": True, "news_list": [news_item.to_dict(
            only=("id", "title", "content", "categories",
                  "creation_time", "modified_date")) for news_item in list_of_news]})

    def post(self):
        args = parse_args()
        session = db_session.create_session()
        news = News(
            id=args["id"],
            title=args["title"],
            content=args["content"],
            categories=args["categories"],
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
                            "error": self.AWARD_ALREADY_EXISTS.format(args['id'])
                            })
        return jsonify({"success": True})
