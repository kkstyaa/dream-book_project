from app import create_app, db
import os

# Импортируем модели, чтобы SQLAlchemy "увидел" их
from app.models import User, Dream, Symbol, DreamSymbol, Statistic, EmotionStat, SymbolStat, GenerationRequest, GeneratedImage, UserImage

app = create_app()

with app.app_context():
    print("🔄 Создание таблиц базы данных...")
    db.create_all()
    print("✅ Таблицы успешно созданы!")
    
    # Создаем необходимые папки, если их нет
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DREAM_IMAGES_FOLDER'], exist_ok=True)
    print("✅ Папки для загрузки файлов созданы!")