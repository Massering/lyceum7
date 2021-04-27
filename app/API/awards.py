from datetime import datetime

from data import db_session
from data.__all_models import Award

from sqlalchemy.exc import InvalidRequestError


# Сообщения об ошибках:
AWARD_NOT_EXIST = "Award with id: '{0}' doesn't exist"
INCORRECT_PARAM_TYPE = "Type of param: {0} is incorrect"


# Т.к. функции по работе с API наград могут импортироваться целиком, то
# чтобы не было путаницы в начале стоит префикс '_'
def _get_award_by_id(award_id: int) -> Award:
    """
    Функция возвращает награду по id, или вызывает HTTPException по коду 404.
    (Функция не является частью API наград, а нужна для его работы)
    """
    session = db_session.create_session()
    result = session.query(Award).filter(Award.id == award_id).one()
    # Закрытие сессии, чтобы не возникало ошибок
    # при попытке изменить/удалить найденый объект
    session.close()
    return result


def get_award(award_id: int) -> dict:
    """Функция возвращает словарь с одной наградой по id.

    :param award_id: ID награды
    :return: Словарь вида вида:
    {"success": True/False,
    "award": *словарь с полями награды*,
    "error": *значение ошибки, если произошла ошибка* (не обязательное поле)}
    """
    # Проверка типа параметра
    if not isinstance(award_id, int):
        return {"success": False,
                "error": INCORRECT_PARAM_TYPE.format(award_id)}
    award = _get_award_by_id(award_id)
    if award is None:
        return {"success": False,
                "error": AWARD_NOT_EXIST.format(award_id)}
    return {"success": True, "award": award.to_dict(
        only=("id", "title", "image_filename",
              "direction", "description", "creation_date"))}


def get_awards() -> dict:
    """Функция возвращает словарь со всеми наградами.

    :return: Словарь вида вида:
    {"awards": *данные* }
    """
    session = db_session.create_session()
    return {"awards": [award.to_dict(
        only=("id", "title", "image_filename", "direction",
              "description", "creation_date"))
            for award in session.query(Award).all()]}


def delete_award(award_id: int) -> dict:
    """Функция удаляет награду по id и возвращает
    словарь с данными результата.

    :param award_id: ID награды, если не указан, то передаются все награды
    :return: Словарь вида:
    {"success": True/False,
    "error": *значение ошибки, если произошла ошибка* (не обязательное поле)}
    """
    award = _get_award_by_id(award_id)
    session = db_session.create_session()
    try:
        session.delete(award)
        session.commit()
    # Обработка случая, если такой награды не существует
    except InvalidRequestError as e:
        return {"success": False, "error": AWARD_NOT_EXIST}
    return {"success": True}


def put_award(award_id: int, new_title: str, new_image_filename: str,
              new_direction: str, new_description: str) -> dict:
    """Функция меняет параметры награды по id на новые
    и возвращает словарь с данными результата.

    :param award_id: ID награды
    :param new_title: Новый заголовок награды
    :param new_image_filename: Новый путь до картинки к награде
    :param new_direction: Новое направление награды
    :param new_description: Новое описание награды
    :return: Словарь вида:
    {"success": True/False,
    "error": *значение ошибки, если произошла ошибка* (не обязательное поле)}
    """
    # Получение новости происходить отдельно
    # Т.к. обычное получение новости через _get_award_by_id закрывает сессию и
    # сохранить изменения не возможно
    session = db_session.create_session()
    award = session.query(Award).filter(Award.id == award_id).one()
    if award is None:
        return {"success": False, "error": NEWS_NOT_EXIST}
    # Переопределение параметров
    award.title = new_title
    award.direction = new_direction
    award.description = new_description
    award.image_filename = new_image_filename
    # Дата редактирования меняется автоматически
    award.modified_date = datetime.now()
    session.commit()
    return {"success": True}


def post_award(title: str, direction: str, description: str,
               image_filename="",
               creation_date=datetime.now(),
               modified_date=datetime.now()) -> None:
    """Функция добавляет награду в БД по переданным параметрам.

    :param title: Заголовок награды
    :param image_filename: Пути к изображению для награды
    :param direction: Направление награды
    :param description: Содержание награды
    :param creation_date: Время создании награды (по умолчанию текущее время)
    :param modified_date: Время последнего изменения награды (по умолчанию текущее время)
    :return: None
    """
    session = db_session.create_session()
    award = Award(
        title=title,
        description=description,
        direction=direction,
        image_filename=image_filename,
        creation_date=creation_date,
        modified_date=modified_date,
    )
    session.add(award)
    session.commit()
