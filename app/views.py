from app import login_manager, app

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
    return render_template('home_page.html', title='Главная')


