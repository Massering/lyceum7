from app import login_manager, app, db_session

from flask import render_template, redirect, abort

from app.data.__all_models import News
from app.data.__all_models import Award


@app.template_filter('format_data')
def format_data(dt):
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

    return f"{dt.day} {months[dt.month - 1]} {dt.year} в {dt.strftime('%H:%M')}"


# помимо 404 будет обрабатываться ещё и попытка перейти на
# панель админа без входа в аккаунт
@login_manager.unauthorized_handler
@app.errorhandler(404)
def handle_404(error=""):
    return render_template("404.html")


@login_manager.unauthorized_handler
@app.errorhandler(413)
def handle_413(error=""):
    return render_template("error.html", error='413', message='Ваш файл слишком большой, вы не можете его прикрепить')


@app.route('/')
@app.route('/index')
def home_page():
    db_sess = db_session.create_session()
    params = {
        "title": "Главная",
        "news_list": sorted(db_sess.query(News).all(),
                            key=lambda i: i.creation_date, reverse=True),
        "split": str.split,
    }
    return render_template('home_page.html', **params)


@app.route('/news')
def news_page():
    db_sess = db_session.create_session()
    params = {
        "title": "Новости",
        "news_list": sorted(db_sess.query(News).all(),
                            key=lambda i: i.creation_date, reverse=True),
        "split": str.split,
    }
    return render_template('news_page.html', **params)


@app.route('/awards')
def awards_page():
    db_sess = db_session.create_session()
    params = {
        "title": "Достижения",
        "awards_list": sorted(db_sess.query(Award).all(),
                              key=lambda i: i.creation_date, reverse=True),
    }
    return render_template('awards_page.html', **params)


@app.route('/admission_to_lyceum')
def admission_to_lyceum():
    params = {
        "title": "Прием в лицей",
    }
    return render_template('admission_to_lyceum.html', **params)


@app.route('/specialized_classes')
def specialized_classes():
    params = {
        "title": "Специализированные классы",
    }
    return render_template('specialized_classes.html', **params)
