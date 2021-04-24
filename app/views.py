from app import login_manager, app, db_session
from data.__all_models import News

from flask import render_template, redirect, abort


# помимо 404 будет обрабатываться ещё и попытка перейти на
# панель админа без входа в аккаунт
@login_manager.unauthorized_handler
@app.errorhandler(404)
def handle_404(error=""):
    return render_template("404.html")


@app.route('/')
@app.route('/index')
def home_page():
    session = db_session.create_session()
    params = {
        "title": "Главная",
        "news_list": session.query(News).all()
    }
    return render_template('home_page.html', **params)


