#Этот файл реализует автоматическое распознавание символов в тексте сна и сохраняет связи между сном и символами в базу данных.

import re
from app.models import db, Symbol, DreamSymbol

def analyze_and_save_symbols(dream_id, content):
    """
    Анализирует текст сна и сохраняет связи с символами
    """
    if not content:
        return
    
    # Получаем все символы из БД
    all_symbols = Symbol.query.all()
    
    if not all_symbols:
        return
    
    found_symbols = []
    content_lower = content.lower()
    
    for symbol in all_symbols:
        # Ищем слово целиком (не часть другого слова)
        pattern = r'\b' + re.escape(symbol.name.lower()) + r'\b'
        if re.search(pattern, content_lower):
            found_symbols.append(symbol)
    
    # Удаляем старые связи
    DreamSymbol.query.filter_by(dream_id=dream_id).delete()
    
    # Добавляем новые
    for symbol in found_symbols:
        dream_symbol = DreamSymbol(dream_id=dream_id, symbol_id=symbol.symbol_id)
        db.session.add(dream_symbol)
    
    db.session.commit()
   