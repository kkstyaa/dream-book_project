#Этот файл отвечает за сбор, расчёт и хранение статистики пользователя. 
#Он вызывается после каждого изменения снов (создание, редактирование, удаление).
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models import Dream, EmotionStat, SymbolStat, Statistic, DreamSymbol, Symbol

def update_all_stats(user_id):
    """Обновляет всю статистику для пользователя"""
    update_emotion_stats(user_id)
    update_symbol_stats(user_id)
    update_cached_statistics(user_id)


def update_emotion_stats(user_id):
    """Обновляет emotion_stats (средняя оценка по дням)"""
    # Очищаем старые данные
    EmotionStat.query.filter_by(user_id=user_id).delete()
    
    # Группируем сны по дате
    results = db.session.query(
        Dream.dream_date,
        func.avg(Dream.mood).label('avg_mood'),
        func.count(Dream.dream_id).label('dream_count')
    ).filter_by(user_id=user_id).group_by(Dream.dream_date).all()
    
    for result in results:
        emotion_stat = EmotionStat(
            user_id=user_id,
            period='day',
            date=result.dream_date,
            avg_mood=float(result.avg_mood) if result.avg_mood else None,
            dream_count=result.dream_count
        )
        db.session.add(emotion_stat)
    
    db.session.commit()


def update_symbol_stats(user_id):
    """Обновляет symbol_stats (частота символов)"""
    SymbolStat.query.filter_by(user_id=user_id).delete()
    
    # Считаем частоту каждого символа
    results = db.session.query(
        DreamSymbol.symbol_id,
        func.count(DreamSymbol.dream_id).label('frequency')
    ).join(Dream, Dream.dream_id == DreamSymbol.dream_id)\
     .filter(Dream.user_id == user_id)\
     .group_by(DreamSymbol.symbol_id).all()
    
    for result in results:
        symbol_stat = SymbolStat(
            user_id=user_id,
            symbol_id=result.symbol_id,
            period='all_time',
            date=datetime.now().date(),
            frequency=result.frequency
        )
        db.session.add(symbol_stat)
    
    db.session.commit()


def update_cached_statistics(user_id):
    """Обновляет кэшированную статистику (JSON)"""
    total_dreams = Dream.query.filter_by(user_id=user_id).count()
    avg_mood = db.session.query(func.avg(Dream.mood)).filter_by(user_id=user_id).scalar()
    
    # Топ-5 символов
    top_symbols = db.session.query(
        Symbol.name,
        func.count(DreamSymbol.symbol_id).label('count')
    ).join(DreamSymbol, DreamSymbol.symbol_id == Symbol.symbol_id)\
     .join(Dream, Dream.dream_id == DreamSymbol.dream_id)\
     .filter(Dream.user_id == user_id)\
     .group_by(Symbol.symbol_id)\
     .order_by(func.count(DreamSymbol.symbol_id).desc())\
     .limit(5).all()
    
    data = {
        'total_dreams': total_dreams,
        'avg_mood': float(avg_mood) if avg_mood else None,
        'top_symbols': [{'name': s.name, 'count': s.count} for s in top_symbols]
    }
    
    # Проверяем, есть ли уже запись
    existing = Statistic.query.filter_by(user_id=user_id, period='all_time').first()
    if existing:
        existing.data = data
        existing.updated_at = datetime.now()
    else:
        statistic = Statistic(
            user_id=user_id,
            period='all_time',
            data=data
        )
        db.session.add(statistic)
    
    db.session.commit()
    