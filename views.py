from config import APP_SETTINGS
from data import db_session
from data.__all_models import Admin
from forms.admin import AdminLoginForm, AdminRegisterForm

from flask import Flask, render_template, redirect, abort
from flask_login import login_user, logout_user, login_required, LoginManager


app = Flask(__name__)
app.config.update(APP_SETTINGS)
# Менеджер логинов (нужно для работы flask_login)
login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/app_data.sqlite")


@login_manager.user_loader
def load_admin(admin_id: int):
    session = db_session.create_session()
    return session.query(Admin).get(admin_id)


@app.route('/')
@app.route('/index')
def home_page():
    return render_template('home_page.html', title='Главная')


# region admin routes
@app.route('/admin/')
@app.route('/admin/index')
@login_required
def admin_page():
    return render_template('admin_page.html')


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
            if session.query(Admin).filter(Admin.login == form.login.data).first():
                return render_template('admin_register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
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


# помимо 404 будет обрабатываться ещё и попытка перейти на
# панель админа без входа в аккаунт
@login_manager.unauthorized_handler
@app.errorhandler(404)
def handle_404(error=""):
    return render_template("404.html")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
