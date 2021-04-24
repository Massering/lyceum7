from app import login_manager, app

from flask import render_template, redirect, abort

from app.data.db_session import create_session
from app.data.__all_models import News
from app.data.__all_models import Award


# помимо 404 будет обрабатываться ещё и попытка перейти на
# панель админа без входа в аккаунт
@login_manager.unauthorized_handler
@app.errorhandler(404)
def handle_404(error=""):
    return render_template("404.html")


@app.route('/')
@app.route('/index')
def home_page():
    db_sess = create_session()
    news = db_sess.query(News).all()
    return render_template('home_page.html', title='Главная', news_list=news).replace('992', '600')


@app.route('/news')
def news_page():
    db_sess = create_session()
    news = db_sess.query(News).all()
    return render_template('news_page.html', title='Новости', news_list=news)


@app.route('/awards')
def awards_page():
    db_sess = create_session()
    awards = db_sess.query(Award).all()
    return render_template('awards_page.html', title='Достижения', awards_list=awards)
