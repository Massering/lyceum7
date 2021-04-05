from config import APP_SETTINGS
from data import db_session
from data.__all_models import *

from flask import Flask, render_template


app = Flask(__name__)
app.config.update(APP_SETTINGS)

db_session.global_init("db/app_data.sqlite")


@app.route('/')
@app.route('/index')
def home_page():
    return render_template('home_page.html', title='Главная')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
