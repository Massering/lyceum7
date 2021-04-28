from app import login_manager, app
from data.__all_models import News, Award
from API.news import get_news
from API.awards import get_awards

from flask import render_template, redirect, abort


# помимо 404 будет обрабатываться ещё и попытка перейти на
# панель админа без входа в аккаунт
@login_manager.unauthorized_handler
@app.errorhandler(404)
def handle_404(error=""):
    return render_template("404.html")


@app.errorhandler(413)
def handle_413(error=""):
    return render_template("error.html", error='413',
                           message='Ваш файл слишком большой, вы не можете его прикрепить')


# Фильтр для преобразования пути до файла с учётом загрузочной директории
@app.template_filter("format_filepath")
def format_filepath(path: str) -> str:
    return os.path.join(app.config["UPLOAD_FOLDER"], path)


@app.route('/')
@app.route('/index')
def home_page():
    params = {
        "title": "Главная",
        "news_list": sorted(get_news()["news"],
                            key=lambda x: x["creation_date"], reverse=True),
        "split": str.split,
    }
    return render_template('home_page.html', **params)


@app.route('/news')
def news_page():
    params = {
        "title": "Новости",
        "news_list": sorted(get_news()["news"],
                            key=lambda x: x["creation_date"], reverse=True),
        "split": str.split,
    }
    return render_template('news_page.html', **params)


@app.route('/awards')
def awards_page():
    params = {
        "title": "Достижения",
        "awards_list": sorted(get_awards()["awards"],
                              key=lambda x: x["creation_date"], reverse=True),
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


@app.route('/school_feed')
def school_feed():
    params = {
        "title": "Школьное питание",
    }
    return render_template('school_feed.html', **params)


@app.route('/rosneft_class')
def rosneft_class():
    params = {
        "title": "Роснефть-класс",
    }
    return render_template('rosneft_class.html', **params)


@app.route('/FoRCaSE')
def forcase():
    params = {
        "title": "ОРКСЭ",
    }
    return render_template('FoRCaSE.html', **params)


@app.route('/standard_of_education_quality')
def standard_of_education_quality():
    params = {
        "title": "Стандарт качества образования",
    }
    return render_template('standard_of_education_quality.html', **params)
