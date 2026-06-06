from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from app.models import db
from flask import send_from_directory

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Для доступа к этой странице необходимо войти в систему'
login_manager.login_message_category = 'warning'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    # Blueprints
    from app.auth import bp as auth_bp
    from app.dreams import bp as dreams_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dreams_bp, url_prefix='/dreams')

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


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

