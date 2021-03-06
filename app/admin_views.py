import os
from datetime import datetime

from app import app, login_manager, db_session
from data.__all_models import Admin
from API.news import *
from API.awards import *
from forms.admin import AdminLoginForm, AdminRegisterForm
from forms.news import NewsForm
from forms.award import AwardForm

from werkzeug.datastructures import CombinedMultiDict, FileStorage
from flask import render_template, redirect, abort, request, url_for
from flask_login import login_required, login_user, logout_user, current_user

USER_SITES = ['/awards', '/news']


# Функция загрузки аккаунта для login_manager
@login_manager.user_loader
def load_admin(admin_id: int):
    session = db_session.create_session()
    return session.query(Admin).filter(Admin.id == admin_id).one()


# Функция получения данных новости специально для карточек в админке
# (Нужно, т.к. для удобства отобрадение наград в админке отличается)
def get_news_for_cards() -> list:
    news_list = []
    for news in sorted(get_news()["news"],
                       key=lambda x: x["creation_date"], reverse=True):
        # Короткое описание для новости, чтобы не занимать много места
        if len(news["content"]) > 30:
            short_description = news["content"][:30] + '...'
        else:
            short_description = news["content"]
        # Определение пути до одной картинки новости, если они есть
        # (Только одна картинка используется для удобства админа)
        news_image_filename = news['paths_to_images'].split(';')[0]
        if news_image_filename:
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], news_image_filename)
        else:
            image_path = ""
        news_list.append({
            "id": news["id"],
            "card_image_path": image_path,
            "title": news["title"],
            "short_description": short_description,
            # Дата изменения
            "modified_date": str(news['modified_date']),
            "creation_date": str(news['creation_date']),
        })
    return news_list


# Фильтр для преобразования пути до файла с учётом загрузочной директории
@app.template_filter("format_filepath")
def format_filepath(path: str) -> str:
    return os.path.join(app.config["UPLOAD_FOLDER"], path)


# region admin
@app.route('/admin/')
@app.route('/admin/index')
@login_required
def admin_page():
    # Параметры для админки
    params = {
        "title": "Страница администратора",
        "news_list": get_news_for_cards(),
        "awards": get_awards()["awards"],
    }
    return render_template('admin_page.html', **params)


@app.route('/admin/logout')
@login_required
def logout_from_admin():
    logout_user()

    if '/'.join([''] + request.referrer.split('/')[3:]) in USER_SITES:
        return redirect(request.referrer)
    return redirect('/')


@app.route('/admin/login', methods=['GET', 'POST'])
def login_to_admin():
    form = AdminLoginForm()
    params = {
        "form": form,
        "title": "Вход",
        "message": "",
    }
    if form.validate_on_submit():
        session = db_session.create_session()
        admin_user = session.query(Admin).filter(Admin.login == form.login.data).first()
        if admin_user and admin_user.check_password(form.password.data):
            login_user(admin_user, remember=form.remember_me.data)
            return redirect('/admin/index')
        params["message"] = "Неправильный логин или пароль"
        return render_template('admin_login.html', **params)
    return render_template('admin_login.html', **params)


@app.route('/admin/register', methods=['GET', 'POST'])
def register_admin():
    # Если включён решим debug или выполнен вход в аккаунт
    # то можно добавить админа, иначе 404
    if app.config.get("DEBUG", False) or current_user.is_authenticated:
        form = AdminRegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('admin_register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            session = db_session.create_session()
            # Проверка на совпадение логина
            if session.query(Admin).filter(Admin.login == form.login.data).first():
                return render_template('admin_register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            # Проверка на совпадение почты
            if session.query(Admin).filter(Admin.email == form.email.data).first():
                return render_template('admin_register.html', title='Регистрация',
                                       form=form,
                                       message="Такая почта уже указана")
            # Добавление аккаунта админа в БД
            admin_user = Admin(
                login=form.login.data,
                surname=form.surname.data,
                name=form.name.data,
                email=form.email.data,
            )
            admin_user.set_password(form.password.data)
            session.add(admin_user)
            session.commit()
            # Перенаправление на вход в аккаунт
            redirect('/admin/login')
        return render_template('admin_register.html', title='Регистрация', form=form)
    abort(404)


# endregion


# Т.к. менять/удалять/добавлять новости может только админ,
# то и соответствующие route'ы находятся здесь
# region news
@app.route('/news/edit/<int:news_id>', methods=["GET", "POST"])
@login_required
def edit_news(news_id):
    # Нужно для загрузки файлов
    # Подробнее: https://flask-wtf.readthedocs.io/en/stable/form.html
    form = NewsForm(CombinedMultiDict((request.files, request.form)))
    news = get_news(news_id)["news"]
    params = {
        "title": "Редактирование новости",
        "message": "",
        "form": form,
    }
    # Установка текущих данных новости (кроме картинок, это не нужно, они
    # выбираются заново), только при GET запросе, чтобы не переопределить новые
    # данные при POST запросе
    if request.method == "GET":
        form.title.data = news["title"]
        form.content.data = news["content"]

    if form.validate_on_submit():
        new_title = form.title.data
        new_content = form.content.data
        # Обработка загруженных файлов
        new_filenames = []
        # Абсолютный путь для загрузки, иначе при загрузке будут ошибки
        app_root = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(app_root, app.config["UPLOAD_FOLDER"])
        for file in form.files_field.data:
            filename = f"news_img/{file.filename}"
            # Проверка на соответствие форматам указанных в конфиге
            # Проверка на соответствие форматам указанных в конфиге
            if filename.split('.')[-1].lower() in app.config["ALLOWED_EXTENSIONS"]:
                # Сохранение файла и добавление пути до него в список
                image_path = os.path.join(upload_dir, filename)
                file.save(image_path)
                new_filenames.append(filename)

        new_paths_to_images = ';'.join(new_filenames)
        # Изменение параметров у новости
        put_news(news_id, new_title, new_content, new_paths_to_images)
        return redirect('/admin')

    return render_template('news_form.html', **params)


@app.route('/news/add', methods=["GET", "POST"])
@login_required
def add_news():
    # Нужно для загрузки файлов
    # Подробнее: https://flask-wtf.readthedocs.io/en/stable/form.html
    form = NewsForm(CombinedMultiDict((request.files, request.form)))
    params = {
        "title": "Добавление новости",
        "message": "",
        "form": form,
    }
    if form.validate_on_submit():
        # Базовые параметры для новости
        title = form.title.data
        content = form.content.data
        # Обработка загруженных файлов
        filenames = []
        # Абсолютный путь для загрузки, иначе при загрузке будут ошибки
        app_root = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(app_root, app.config["UPLOAD_FOLDER"])
        for file in form.files_field.data:
            # Имя файла содержит id новости, чтобы при большом количестве новостей
            # картинки с одинаковыми именами не перезаписывали друг друга
            filename = f"news_img/{file.filename}"
            # Проверка на соответствие форматам указанных в конфиге
            if filename.split('.')[-1].lower() in app.config["ALLOWED_EXTENSIONS"]:
                # Сохранение файла и добавление пути до него в список
                image_path = os.path.join(upload_dir, filename)
                file.save(image_path)
                filenames.append(filename)

        paths_to_images = ';'.join(filenames)
        # Добавление новости
        post_news(title, content, paths_to_images)
        return redirect('/admin')
    return render_template('news_form.html', **params)


@app.route('/news/delete/<int:news_id>')
@login_required
def delete_news_route(news_id: int):
    # Удаление новости
    delete_news(news_id)
    return redirect('/admin')


# Т.к. менять/удалять/добавлять награды может только админ,
# то и соответствующие route'ы находятся здесь
# region awards
@app.route('/award/edit/<int:award_id>', methods=["GET", "POST"])
@login_required
def edit_award(award_id):
    # Нужно для загрузки файлов
    # Подробнее: https://flask-wtf.readthedocs.io/en/stable/form.html
    form = AwardForm(CombinedMultiDict((request.files, request.form)))
    award = get_award(award_id)["award"]
    params = {
        "title": "Редактирование награды",
        "message": "",
        "form": form,
    }
    # Установка текущих данных награды (кроме картинки, это не нужно, она
    # выбирается заново), только при GET запросе, чтобы не переопределить
    # данные при POST запросе
    if request.method == "GET":
        form.title.data = award["title"]
        form.direction.data = award["direction"]
        form.description.data = award["description"]

    if form.validate_on_submit():
        # Новые данные
        new_title = form.title.data
        new_direction = form.direction.data
        new_description = form.description.data
        # Обработка загруженного файла
        # Абсолютный путь для загрузки, иначе при загрузке будут ошибки
        app_root = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(app_root, app.config["UPLOAD_FOLDER"])
        # Получение файла и его имени
        file = form.file_field.data
        # Проверка на соответствие форматам указанных в конфиге
        if file.filename.split('.')[-1].lower() in app.config["ALLOWED_EXTENSIONS"]:
            new_filename = f"award_img/{file.filename}"
            # Сохранение файла и добавление пути до него в список
            image_path = os.path.join(upload_dir, new_filename)
            file.save(image_path)
            new_image_filename = new_filename
        else:
            new_image_filename = ""

        # Изменение параметров у награды
        put_award(award_id, new_title, new_image_filename,
                  new_direction, new_description)
        return redirect('/admin')

    return render_template('award_form.html', **params)


@app.route('/award/add', methods=["GET", "POST"])
@login_required
def add_award():
    # Нужно для загрузки файлов
    # Подробнее: https://flask-wtf.readthedocs.io/en/stable/form.html
    form = AwardForm(CombinedMultiDict((request.files, request.form)))
    params = {
        "title": "Добавление награды",
        "message": "",
        "form": form,
    }
    if form.validate_on_submit():
        # Базовые параметры
        title = form.title.data
        direction = form.direction.data
        description = form.description.data
        # Обработка загруженного файла
        # Абсолютный путь для загрузки, иначе при загрузке будут ошибки
        app_root = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(app_root, app.config["UPLOAD_FOLDER"])
        # Получение файла и его имени
        file = form.file_field.data
        # Проверка на соответствие форматам указанных в конфиге
        if file.filename.split('.')[-1].lower() in app.config["ALLOWED_EXTENSIONS"]:
            filename = f"award_img/{file.filename}"
            # Сохранение файла и добавление пути до него в список
            image_path = os.path.join(upload_dir, filename)
            file.save(image_path)
            image_filename = filename
        else:
            image_filename = ""
        # Добавление награды
        post_award(title, direction, description, image_filename)
        return redirect('/admin')
    return render_template('award_form.html', **params)


@app.route('/award/delete/<int:award_id>')
@login_required
def delete_award_route(award_id: int):
    # Удаление награды
    delete_award(award_id)
    return redirect('/admin')
# endregion
