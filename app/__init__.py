from app.data import db_session

from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv


dotenv_path = '.env'
load_dotenv(dotenv_path)

# Создание приложения
app = Flask(__name__)
# Установка конфига учитывая состояние (продакш, разработка, тестирование).
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
elif app.config["ENV"] == "development":
    app.config.from_object("config.DevelopmentConfig")
else:
    app.config.from_object("config.TestingConfig")
# Менеджер логинов (нужно для работы flask_login)
login_manager = LoginManager()
login_manager.init_app(app)
# Инициализация БД
db_session.global_init("app/db/app_data.sqlite")

from app import views
from app import admin_views
