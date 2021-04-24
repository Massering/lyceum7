from .award_parser import parse_args

from data import db_session
from data.__all_models import Award

from flask import jsonify
from flask_restful import Resource
from sqlalchemy.exc import InvalidRequestError, IntegrityError


def get_award_by_id(award_id: int):
    """
    Функция возвращает достижение по id, или
     вызывает HTTPException по коду 404
    """
    session = db_session.create_session()
    result = session.query(Award).get(award_id)
    if result is None:
        abort(404)
        return
    return result


class AwardResource(Resource):
    """Класс представляющий ресурс одного достижения Award"""

    # Сообщения об ошибках:
    AWARD_ALREADY_DELETED = "Award with id: '{0}' has already deleted"

    def get(self, award_id: int):
        award = get_award_by_id(award_id)
        return jsonify({"success": True, "news": award.to_dict(
            only=("id", "title", "image_filename",
                  "direction", "description", "creation_date"))})

    def delete(self, award_id: int):
        award = get_award_by_id(award_id)
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
        awards_list = session.query(Award).all()
        return jsonify({"success": True, "awards_list": [award.to_dict(
            only=("id", "title", "image_filename",
                  "direction", "description", "creation_date")) for award in awards_list]})

    def post(self):
        args = parse_args()
        session = db_session.create_session()
        news = News(
            id=args["id"],
            title=args["title"],
            image_filename=args["image_filename"],
            direction=args["direction"],
            description=args["description"],
            creation_date=args["creation_date"],
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
