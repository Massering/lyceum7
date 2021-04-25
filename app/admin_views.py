import os
from datetime import datetime

from app import app, login_manager, db_session
from data.__all_models import Admin, News
from API.news import *
from API.awards import *
from forms.admin import AdminLoginForm, AdminRegisterForm
from forms.news import NewsForm

from werkzeug.datastructures import CombinedMultiDict, FileStorage
from flask import render_template, redirect, abort, request
from flask_login import login_required, login_user, logout_user

USER_SITES = ['/awards', '/news']


@login_manager.user_loader
def load_admin(admin_id: int):
    session = db_session.create_session()
    return session.query(Admin).get(admin_id)


@app.route('/admin/')
@app.route('/admin/index')
@login_required
def admin_page():
    news_list = []
    for news in sorted(get_news().get("news", []), key=lambda i: i['id'], reverse=True):
        # Короткое описание для новости, чтобы не занимать много места
        if len(news["content"]) > 30:
            short_description = news["content"][:30] + '...'
        else:
            short_description = news["content"]
        # Определение пути до одной картинки новости, если они есть
        # (Только одна картинка используется для удобства админа)
        news_image_filename = news["paths_to_images"].split(';')[0]
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
    params = {
        "title": "Страница админа",
        "news_list": news_list,
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
    if form.validate_on_submit():
        session = db_session.create_session()
        admin_user = session.query(Admin).filter(Admin.login == form.login.data).first()
        if admin_user and admin_user.check_password(form.password.data):
            login_user(admin_user, remember=form.remember_me.data)
            return redirect('/admin/index')
        return render_template('admin_login.html', form=form, title='Вход',
                               message="Неправильный логин или пароль")
    return render_template('admin_login.html', title='Вход', form=form)


@app.route('/admin/register', methods=['GET', 'POST'])
def register_admin():
    # Если включён решим debug, то можно добавить админа, иначе 404
    if app.config.get("DEBUG", False):
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


# Т.к. менять/удалять/добавлять новости может только админ,
# то и соответствующие route'ы находятся здесь
# region news
@app.route('/news/edit/<int:news_id>', methods=["GET", "POST"])
@login_required
def edit_news(news_id):
    # Нужно для работы поля MultipleFileField при загрузке файлов
    # Подробнее: https://flask-wtf.readthedocs.io/en/stable/form.html
    form = NewsForm(CombinedMultiDict((request.files, request.form)))
    params = {
        "title": "Редактирование новости",
        "message": "",
        "form": form,
    }
    if form.validate_on_submit():
        # Создание новости с параметрами
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        news.title = form.title.data
        news.content = form.content.data
        # Обработка загруженных файлов
        filenames = []
        # Абсолютный путь для загрузки, иначе при загрузке будут ошибки
        app_root = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(app_root, app.config["UPLOAD_FOLDER"])
        print(form.files_field.data[0])
        for file in form.files_field.data:
            filename = file.filename
            # Проверка на соответствие форматам указанных в конфиге
            # Проверка на соответствие форматам указанных в конфиге
            if filename.split('.')[-1].lower() in app.config["ALLOWED_EXTENSIONS"]:
                # Сохранение файла и добавление пути до него в список
                try:
                    image_path = os.path.join(upload_dir, filename)
                    file.save(image_path)
                # Исключение появляется, если размер файла превышает
                # app.config["MAX_CONTENT_LENGTH"], т.к. в этом случае файл не
                # сохраняется и его не получается найти, в результате FileNotFoundError
                except FileNotFoundError:
                    params["message"] = "Загружаемый файл слишком большой"
                    return render_template('news_form.html', **params)
                else:
                    filenames.append(filename)

        news.paths_to_images = ';'.join(filenames)
        # Добавление новости
        session.commit()
        return redirect('/admin')

    session = db_session.create_session()
    news = session.query(News).get(news_id)
    form.title.data = news.title
    form.content.data = news.content

    # TODO: Обратное прикрепление файлов
    # Обработка загруженных файлов
    form.files_field.data = []
    for filename in news.paths_to_images.split(';'):
        if filename:
            # Абсолютный путь для загрузки, иначе при загрузке будут ошибки
            app_root = os.path.dirname(os.path.abspath(__file__))
            upload_dir = os.path.join(app_root, app.config["UPLOAD_FOLDER"])

            file_content = open(upload_dir + '\\' + filename, 'r')
            file = FileStorage(file_content, filename, file_content.name, "image/" + filename.split('.')[-1],
                               os.path.getsize(upload_dir + '\\' + filename))
            print(file, file.headers)

            form.files_field.data.append(file)

    return render_template('news_form.html', **params)


@app.route('/news/add', methods=["GET", "POST"])
@login_required
def add_news():
    # Нужно для работы поля MultipleFileField при загрузке файлов
    # Подробнее: https://flask-wtf.readthedocs.io/en/stable/form.html
    form = NewsForm(CombinedMultiDict((request.files, request.form)))
    params = {
        "title": "Добавление новости",
        "message": "",
        "form": form,
    }
    if form.validate_on_submit():
        # Создание новости с параметрами
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        # Обработка загруженных файлов
        filenames = []
        # Абсолютный путь для загрузки, иначе при загрузке будут ошибки
        app_root = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(app_root, app.config["UPLOAD_FOLDER"])
        for file in form.files_field.data:
            filename = file.filename
            # Проверка на соответствие форматам указанных в конфиге
            # Проверка на соответствие форматам указанных в конфиге
            if filename.split('.')[-1].lower() in app.config["ALLOWED_EXTENSIONS"]:
                # Сохранение файла и добавление пути до него в список
                try:
                    image_path = os.path.join(upload_dir, filename)
                    file.save(image_path)
                # Исключение появляется, если размер файла превышает
                # app.config["MAX_CONTENT_LENGTH"], т.к. в этом случае файл не
                # сохраняется и его не получается найти, в результате FileNotFoundError
                except FileNotFoundError as e:
                    params["message"] = "Загружаемый файл слишком большой"
                    return render_template('news_form.html', **params)
                else:
                    filenames.append(filename)

        news.paths_to_images = ';'.join(filenames)
        # Добавление новости
        session = db_session.create_session()
        session.add(news)
        session.commit()
        return redirect('/admin')
    return render_template('news_form.html', **params)


@app.route('/news/delete/<int:news_id>')
@login_required
def delete_news_route(news_id: int):
    # Удаление новости
    delete_news(news_id)
    return redirect(request.referrer)
# endregion


# Т.к. менять/удалять/добавлять награды может только админ,
# то и соответствующие route'ы находятся здесь
# region awards
# TODO: П А М А Г И Т Е
# endregion
