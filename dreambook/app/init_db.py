from app import create_app, db
from app.models import User, Dream, Symbol, DreamSymbol, Statistic, EmotionStat, SymbolStat, GenerationRequest, GeneratedImage, UserImage
import os

app = create_app()

with app.app_context():
    print("🔄 Проверка и создание таблиц базы данных...")
    db.create_all()
    print("✅ Таблицы готовы!")
    
    # Создаём папки
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DREAM_IMAGES_FOLDER'], exist_ok=True)
    print("✅ Папки для загрузки готовы!")
    
    # Проверим, есть ли хоть один пользователь
    if User.query.count() == 0:
        print("⚠️ В базе нет пользователей. Создайте первого через регистрацию.")