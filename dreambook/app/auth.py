from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from app.utils import save_file
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/auth')

def admin_required(func):
    """Декоратор для проверки прав администратора"""
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('У вас нет доступа к этой странице', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')
        remember = request.form.get('remember')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        flash('Неверный логин или пароль', 'danger')

    return render_template('auth/login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('login')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким логином уже существует', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'danger')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('index'))

    return render_template('auth/register.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


@bp.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Файл не выбран', 'danger')
        return redirect(url_for('profile'))

    file = request.files['avatar'] #Получает загруженный файл из формы
    filename = save_file(file, current_app.config['AVATAR_FOLDER']) #Сохраняет файл в папку

    if filename:
        #Обновляет поле avatar_url у текущего пользователя
        current_user.avatar_url = f'/uploads/avatars/{filename}'
        db.session.commit()
        flash('Аватар успешно обновлён!', 'success')
    else:
        flash('Недопустимый формат файла', 'danger')

    return redirect(url_for('profile'))