import os
from datetime import datetime

from app import app, login_manager, db_session
from data.__all_models import Admin, News
from forms.admin import AdminLoginForm, AdminRegisterForm
from forms.news import NewsForm

import requests
from werkzeug.utils import secure_filename
from flask import render_template, redirect, abort, send_from_directory, request
from flask_login import login_required, login_user, logout_user


@login_manager.user_loader
def load_admin(admin_id: int):
    session = db_session.create_session()
    return session.query(Admin).get(admin_id)


@app.route('/admin/')
@app.route('/admin/index')
@login_required
def admin_page():
    news_list = []
    session = db_session.create_session()
    for news in session.query(News).all():
        # Короткое описание для новости, чтобы не занимать много места
        if len(news.content) > 30:
            short_description = news.content[:30] + '...'
        else:
            short_description = news.content
        news_list.append({
            "card_image_path": "",
            "title": news.title,
            "short_description": short_description,
            # Дата изменения
            "modified_date": f"{news.modified_date:%H:%M:%S %Y-%m-%d}",
            "creation_time": f"{news.creation_time:%H:%M:%S %Y-%m-%d}",
        })
    params = {
        "news_list": news_list,
    }
    return render_template('admin_page.html', **params)


@app.route('/admin/logout')
@login_required
def logout_from_admin():
    logout_user()
    return redirect("/")


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
@app.route('/news/edit/<int:news_id>')
@login_required
def edit_news(news_id):
    # Получение новости
    # TODO: выглядит как мусор, лучше сделать что-нибудь лучше
    news = requests.get(f"news/{news_id}")
    # TODO: template с формой, где будет редактирование
    return None


@app.route('/news/add', methods=["GET", "POST"])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        # Создание новости с параметрами
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        # Обработка загруженных файлов из request.files
        filenames = []
        files = request.files.getlist("files_field")
        print(files)
        print(form.files_field)
        print(form.files_field.data)
        for file in files:
            print(file)
            print("FUCK YOU")
            # Получение безопасного имени файла (подробнее в описании secure_filename)
            filename = secure_filename(file.filename)
            # TODO: убедится, что в ALLOWED_EXTENSIONS нет фигни
            if file and filename.split('.')[-1] in app.config["ALLOWED_EXTENSIONS"]:
                # Сохранение файла и добавление пути до него в список
                print(app.config['UPLOAD_FOLDER'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filenames.append(filename)
        news.paths_to_images = ';'.join(filenames)
        # Добавление новости
        session = db_session.create_session()
        session.add(news)
        session.commit()
        return redirect('/admin/')
    params = {
        "message": "",
        "form": form,
        "news_data": []
    }
    return render_template('news_form.html', **params)
# endregion


# Т.к. менять/удалять/добавлять награды может только админ,
# то и соответствующие route'ы находятся здесь
# region awards
# TODO: П А М А Г И Т Е
# endregion
