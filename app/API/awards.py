from datetime import datetime

from data import db_session
from data.__all_models import Award

from sqlalchemy.exc import InvalidRequestError, IntegrityError


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
    result = session.query(Award).get(award_id)
    # Закрытие сессии, чтобы не возникало ошибок
    # при попытке изменить/удалить найденый объект
    session.close()
    return result


def get(award_id=-1) -> dict:
    """Функция возвращает словарь со всеми наградами,
    либо словарь с одной наградой, если указан её id.

    :param award_id: ID награды, если не указан, то передаются все награды
    :return: Словарь вида вида:
    {"success": True/False,
    "award": *либо одна награда или список с наградами в виде словаря*,
    "error": *значение ошибки, если произошла ошибка* (не обязательное поле)}
    """
    session = db_session.create_session()
    # Проверка указан ли id
    if award_id == -1:
        # Словарб со всеми наградами
        return {"success": True,
                "award": [award.to_dict(
                    only=("id", "title", "image_filename",
                          "direction", "description", "creation_date"))
                    for award in session.query(Award).all()]}
    # Проверка типа
    elif not isinstance(award_id, int):
        return {"success": False,
                "error": INCORRECT_PARAM_TYPE.format(award_id)}
    # Возвращение словаря с наградой по id если она существует
    award = _get_award_by_id(award_id)
    if award is None:
        return {"success": False,
                "error": AWARD_NOT_EXIST.format(award_id)}
    return {"success": True, "award": award.to_dict(
        only=("id", "title", "image_filename",
              "direction", "description", "creation_date"))}


def delete(award_id: int) -> dict:
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


def put(award_id: int, new_title: str, new_image_filename: str,
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
    # Получение награды и переопределение параметров
    award = _get_award_by_id(award_id)
    if award is None:
        return {"success": False, "error": AWARD_NOT_EXIST}
    award.title = new_title
    award.image_filename = new_image_filename
    award.direction = new_direction
    award.description = new_description
    # Дата редактирования меняется автоматически
    award.modified_date = datetime.now()
    session.commit()
    return {"success": True}


def post(title: str, image_filename: str,
         direction: str, description: str,
         creation_time=datetime.now(),
         modified_date=datetime.now()) -> None:
    """Функция добавляет награду в БД по переданным параметрам.

    :param title: Заголовок награды
    :param image_filename: Пути к изображению для награды
    :param direction: Направление награды
    :param description: Содержание награды
    :param creation_time: Время создании награды (по умолчанию текущее время)
    :param modified_date: Время последнего изменения награды (по умолчанию текущее время)
    :return: None
    """
    session = db_session.create_session()
    award = Award(
        title=title,
        description=description,
        direction=direction,
        image_filename=image_filename,
        creation_time=creation_time,
        modified_date=modified_date,
    )
    session.add(award)
    session.commit()
