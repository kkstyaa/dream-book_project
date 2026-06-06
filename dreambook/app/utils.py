import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """Проверка разрешённого расширения файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, folder):
    """Сохраняет файл и возвращает его имя"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Генерируем уникальное имя файла
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    
    filepath = os.path.join(folder, filename)
    file.save(filepath)
    
    return filename

def generate_ai_image(prompt):
    """
    Генерирует изображение через API Pollinations.ai
    Возвращает URL сохранённого файла или None
    """
    try:
        # Формируем запрос
        encoded_prompt = requests.utils.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        # Получаем изображение
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # Генерируем уникальное имя файла
            filename = f"{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(current_app.config['DREAM_IMAGES_FOLDER'], filename)
            
            # Сохраняем файл
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return f'/uploads/dream_images/{filename}'
        
        return None
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        return None