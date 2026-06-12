from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from app.models import db
from flask import send_from_directory


login_manager = LoginManager()
login_manager.login_view = 'auth.login' #куда перенаправлять неавторизованных
login_manager.login_message = 'Для доступа к этой странице необходимо войти в систему' # сообщение при попытке доступа
login_manager.login_message_category = 'warning'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app) #подключаем бд
    Migrate(app, db)
    login_manager.init_app(app) #подключение системы идентификации 

    # Blueprints
    from app.auth import bp as auth_bp 
    from app.dreams import bp as dreams_bp
    from app.statistics import bp as stats_bp
    from app.admin import bp as admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth') # маршруты: /auth/login, /auth/logout
    app.register_blueprint(dreams_bp, url_prefix='/dreams')  # маршруты: /dreams/, /dreams/new
    app.register_blueprint(stats_bp, url_prefix='/statistics') # /statistics/
    app.register_blueprint(admin_bp, url_prefix='/admin') # /admin/users, /admin/symbols

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/profile')
    def profile():
        return render_template('profile.html')
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app

#Загрузка пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

