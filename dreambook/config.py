import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret')
    # Временный SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dream_book.db'

    # Отключает отслеживание изменений
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Настройки загрузки файлов
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    AVATAR_FOLDER = os.path.join(UPLOAD_FOLDER, 'avatars')
    DREAM_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'dream_images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}