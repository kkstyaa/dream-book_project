from flask import Blueprint, render_template, Response
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Dream, DreamSymbol, Symbol, Statistic
import csv
from io import StringIO

bp = Blueprint('statistics', __name__, url_prefix='/statistics')


@bp.route('/')
@login_required
def index():
    user_id = current_user.user_id
    
    # Пробуем взять из кэша
    cached = Statistic.query.filter_by(user_id=user_id, period='all_time').first()
    
    if cached and cached.data:
        data = cached.data
        total_dreams = data.get('total_dreams', 0)
        avg_mood = data.get('avg_mood')
        top_symbols = data.get('top_symbols', [])
    else:
        # Если кэша нет — считаем на лету
        total_dreams = Dream.query.filter_by(user_id=user_id).count()
        avg_mood = db.session.query(func.avg(Dream.mood)).filter_by(user_id=user_id).scalar()
        top_symbols = []
    
    monthly_counts = db.session.query(
        func.strftime('%Y-%m', Dream.dream_date).label('month'),
        func.count(Dream.dream_id).label('count')
    ).filter_by(user_id=user_id).group_by('month').order_by('month').all()
    
    monthly_moods = db.session.query(
        func.strftime('%Y-%m', Dream.dream_date).label('month'),
        func.avg(Dream.mood).label('avg_mood')
    ).filter_by(user_id=user_id).group_by('month').order_by('month').all()
    
    monthly_counts_list = [{'month': m.month, 'count': m.count} for m in monthly_counts]
    monthly_moods_list = [{'month': m.month, 'avg_mood': round(m.avg_mood, 1) if m.avg_mood else 0} for m in monthly_moods]
    
    total_months = len(monthly_counts_list)
    
    best_month = None
    if monthly_counts_list:
        best = max(monthly_counts_list, key=lambda x: x['count'])
        best_month = {'month': best['month'], 'count': best['count']}
    
    # Все символы для облака тегов
    all_symbols = db.session.query(
        Symbol.name,
        func.count(DreamSymbol.symbol_id).label('count')
    ).join(DreamSymbol, DreamSymbol.symbol_id == Symbol.symbol_id)\
     .join(Dream, Dream.dream_id == DreamSymbol.dream_id)\
     .filter(Dream.user_id == user_id)\
     .group_by(Symbol.symbol_id)\
     .order_by(func.count(DreamSymbol.symbol_id).desc()).all()
    
    all_symbols_list = [{'name': s.name, 'count': s.count} for s in all_symbols]
    
    return render_template('statistics/index.html',
                         total_dreams=total_dreams,
                         avg_mood=avg_mood,
                         total_months=total_months,
                         best_month=best_month,
                         monthly_counts=monthly_counts_list,
                         monthly_moods=monthly_moods_list,
                         top_symbols=top_symbols,
                         all_symbols=all_symbols_list)


@bp.route('/export/stats')
@login_required
def export_stats():
    """Экспорт сводной статистики в CSV"""
    user_id = current_user.user_id
    from sqlalchemy import func
    
    # Общая статистика
    total_dreams = Dream.query.filter_by(user_id=user_id).count()
    avg_mood = db.session.query(func.avg(Dream.mood)).filter_by(user_id=user_id).scalar()
    
    # Самый частый символ
    top_symbol = db.session.query(
        Symbol.name,
        func.count(DreamSymbol.symbol_id).label('count')
    ).join(DreamSymbol, DreamSymbol.symbol_id == Symbol.symbol_id)\
     .join(Dream, Dream.dream_id == DreamSymbol.dream_id)\
     .filter(Dream.user_id == user_id)\
     .group_by(Symbol.symbol_id)\
     .order_by(func.count(DreamSymbol.symbol_id).desc())\
     .first()
    
    top_symbol_name = top_symbol.name if top_symbol else '—'
    top_symbol_count = top_symbol.count if top_symbol else 0
    
    # Количество снов по месяцам
    monthly_counts = db.session.query(
        func.strftime('%Y-%m', Dream.dream_date).label('month'),
        func.count(Dream.dream_id).label('count')
    ).filter_by(user_id=user_id).group_by('month').order_by('month').all()
    
    # Топ-5 символов
    top5_symbols = db.session.query(
        Symbol.name,
        func.count(DreamSymbol.symbol_id).label('count')
    ).join(DreamSymbol, DreamSymbol.symbol_id == Symbol.symbol_id)\
     .join(Dream, Dream.dream_id == DreamSymbol.dream_id)\
     .filter(Dream.user_id == user_id)\
     .group_by(Symbol.symbol_id)\
     .order_by(func.count(DreamSymbol.symbol_id).desc())\
     .limit(5).all()
    
    si = StringIO()
    cw = csv.writer(si, delimiter=';')
    
    # Общая статистика
    cw.writerow(['ОБЩАЯ СТАТИСТИКА'])
    cw.writerow(['Всего снов', total_dreams])
    cw.writerow(['Средняя оценка настроения', f'{avg_mood:.1f}' if avg_mood else '—'])
    cw.writerow(['Самый частый символ', f'{top_symbol_name} ({top_symbol_count} раз)'])
    cw.writerow([])
    
    # Статистика по месяцам
    cw.writerow(['СТАТИСТИКА ПО МЕСЯЦАМ'])
    cw.writerow(['Месяц', 'Количество снов'])
    for m in monthly_counts:
        cw.writerow([m.month, m.count])
    cw.writerow([])
    
    # Топ-5 символов
    cw.writerow(['ТОП-5 СИМВОЛОВ'])
    cw.writerow(['Символ', 'Частота'])
    for s in top5_symbols:
        cw.writerow([s.name, s.count])
    
    output = si.getvalue()
    try:
        output_bytes = output.encode('windows-1251')
    except:
        output_bytes = output.encode('utf-8-sig')
    
    return Response(
        output_bytes,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=statistics_export.csv'}
    )


@bp.route('/export/dreams')
@login_required
def export_dreams():
    """Экспорт всех снов (книги) в CSV"""
    user_id = current_user.user_id
    dreams = Dream.query.filter_by(user_id=user_id).order_by(Dream.dream_date.desc()).all()
    
    si = StringIO()
    cw = csv.writer(si, delimiter=';')
    cw.writerow(['ID', 'Заголовок', 'Дата сна', 'Настроение (1-5)', 'Текст сна', 'Дата создания'])
    
    for dream in dreams:
        cw.writerow([
            dream.dream_id,
            dream.title,
            dream.dream_date.strftime('%d.%m.%Y'),
            dream.mood or '',
            dream.content[:200] + '...' if len(dream.content) > 200 else dream.content,
            dream.created_at.strftime('%d.%m.%Y %H:%M')
        ])
    
    output = si.getvalue()
    try:
        output_bytes = output.encode('windows-1251')
    except:
        output_bytes = output.encode('utf-8-sig')
    
    return Response(
        output_bytes,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=dreams_export.csv'}
    )