from datetime import datetime

from data import db_session
from data.__all_models import News

from sqlalchemy.exc import InvalidRequestError


# Сообщения об ошибках:
NEWS_NOT_EXIST = "News with id: '{0}' doesn't exist"
INCORRECT_PARAM_TYPE = "Type of param: {0} is incorrect"


# Т.к. функции по работе с API новостей могут импортироваться целиком, то
# чтобы не было путаницы в начале стоит префикс '_'
def _get_news_by_id(news_id: int):
    """
    Функция возвращает новость по id, или вызывает HTTPException по коду 404.
    (Функция не является частью API новостей, а нужна для его работы)
    """
    session = db_session.create_session()
    result = session.query(News).filter(News.id == news_id).one()
    # Закрытие сессии, чтобы не возникало ошибок
    # при попытке изменить/удалить найденый объект
    session.close()
    return result


def get_news(news_id=-1) -> dict:
    """Функция возвращает словарь со всеми новостями,
    либо словарь с одной новостью, если указан её id.

    :param news_id: ID новости, если не указан, то передаются все новости
    :return: Словарь вида:
    {"success": True/False,
    "news": *либо одна новость или список с новостями в виде словаря*,
    "error": *значение ошибки, если произошла ошибка* (не обязательное поле)}
    """
    session = db_session.create_session()
    # Проверка указан ли id
    if news_id == -1:
        # Словарь со всеми новостями
        return {"success": True,
                "news": [news_item.to_dict(
                    only=("id", "title", "content", "paths_to_images",
                          "creation_date", "modified_date"))
                    for news_item in session.query(News).all()]}
    # Проверка типа
    elif not isinstance(news_id, int):
        return {"success": False,
                "news": [],
                "error": INCORRECT_PARAM_TYPE.format(news_id)}
    # Возвращение словаря с новостью по id если она существует
    news = _get_news_by_id(news_id)
    if news is None:
        return {"success": False,
                "news": [],
                "error": NEWS_NOT_EXIST.format(news_id)}
    return {"success": True, "news": news.to_dict(
        only=("id", "title", "content", "paths_to_images",
              "creation_date", "modified_date"))}


def delete_news(news_id: int):
    """Функция удаляет новость по id и возвращает
    словарь с данными результата

    :param news_id: ID новости, если не указан, то передаются все новости
    :return: словарь вида:
    {"success": True/False,
    "error": *значение ошибки, если произошла ошибка* (не обязательное поле)}
    """
    news = _get_news_by_id(news_id)
    session = db_session.create_session()
    try:
        session.delete(news)
        session.commit()
    # Обработка случая, если такой новости не существует
    except InvalidRequestError as e:
        print(e)
        return {"success": False, "error": NEWS_NOT_EXIST}
    return {"success": True}


def put_news(news_id: int, new_title: str, new_content: str, new_paths_to_images: str):
    """Функция меняет параметры новости по id на новые
    и возвращает словарь с данными результата.

    :param news_id: ID новости
    :param new_title: Новый заголовок новости
    :param new_content: Новое содержание новости
    :param new_paths_to_images: Новые пути к изображениям для новости
    :return: словарь вида:
    {"success": True/False,
    "error": *значение ошибки, если произошла ошибка* (не обязательное поле)}
    """
    # Получение новости происходить отдельно
    # Т.к. обычное получение новости через _get_news_by_id закрывает сессию и
    # сохранить изменения не возможно
    session = db_session.create_session()
    news = session.query(News).filter(News.id == news_id).one()
    if news is None:
        return {"success": False, "error": NEWS_NOT_EXIST}
    # Переопределение параметров
    news.title = new_title
    news.content = new_content
    news.paths_to_images = new_paths_to_images
    # Дата редактирования меняется автоматически
    news.modified_date = datetime.now()
    session.commit()
    return {"success": True}


def post_news(title: str, content: str, paths_to_images="",
              creation_date=datetime.now(),
              modified_date=datetime.now()) -> None:
    """Функция добавляет новость в БД по переданным параметрам.

    :param title: Заголовок новости
    :param content: Содержание новости
    :param paths_to_images: Пути к изображениям для новости
    :param creation_date: Время создании новости (по умолчанию текущее время)
    :param modified_date: Время последнего изменения новости (по умолчанию текущее время)
    :return: None
    """
    session = db_session.create_session()
    news = News(
        title=title,
        content=content,
        creation_date=creation_date,
        paths_to_images=paths_to_images,
        modified_date=modified_date,
    )
    session.add(news)
    session.commit()
