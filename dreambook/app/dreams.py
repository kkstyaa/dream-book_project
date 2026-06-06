from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Dream, UserImage, GeneratedImage
from app.utils import save_file, generate_ai_image

bp = Blueprint('dreams', __name__, url_prefix='/dreams')


@bp.route('/')
@login_required
def index():
    """Список снов текущего пользователя с пагинацией"""
    page = request.args.get('page', 1, type=int)
    per_page = 9
    
    pagination = Dream.query.filter_by(user_id=current_user.user_id)\
        .order_by(Dream.dream_date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    dreams = pagination.items
    
    return render_template('dreams/index.html', 
                         dreams=dreams, 
                         pagination=pagination)


@bp.route('/<int:dream_id>')
@login_required
def show(dream_id):
    """Просмотр одного сна"""
    dream = Dream.query.get_or_404(dream_id)
    if dream.user_id != current_user.user_id:
        flash('У вас нет доступа к этому сну', 'danger')
        return redirect(url_for('dreams.index'))
    return render_template('dreams/show.html', dream=dream)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Создание нового сна"""
    # Получаем временную сгенерированную картинку из сессии
    temp_generated_image = session.pop('temp_generated_image', None)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        dream_date = datetime.strptime(request.form.get('dream_date'), '%Y-%m-%d').date()
        mood = request.form.get('mood', type=int)
        generated_image_url = request.form.get('generated_image_url')
        user_image_file = request.files.get('user_image')

        dream = Dream(
            user_id=current_user.user_id,
            title=title,
            content=content,
            dream_date=dream_date,
            mood=mood
        )
        
        db.session.add(dream)
        db.session.flush()  # Получаем dream.dream_id
        
        # Приоритет: если есть загруженная пользователем картинка — используем её
        if user_image_file and user_image_file.filename:
            filename = save_file(user_image_file, current_app.config['DREAM_IMAGES_FOLDER'])
            if filename:
                # Удаляем старую картинку, если есть
                if dream.user_image:
                    db.session.delete(dream.user_image)
                user_image = UserImage(
                    dream_id=dream.dream_id,
                    user_id=current_user.user_id,
                    image_url=f'/uploads/dream_images/{filename}'
                )
                db.session.add(user_image)
        elif generated_image_url or temp_generated_image:
            # Используем сгенерированную картинку
            final_url = generated_image_url or temp_generated_image
            if dream.generated_image:
                dream.generated_image.image_url = final_url
            else:
                gen_image = GeneratedImage(
                    dream_id=dream.dream_id,
                    image_url=final_url
                )
                db.session.add(gen_image)
        
        db.session.commit()
        flash('Сон успешно добавлен!', 'success')
        return redirect(url_for('dreams.index'))

    return render_template('dreams/form.html', dream=None, temp_generated_image=temp_generated_image)


@bp.route('/<int:dream_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(dream_id):
    """Редактирование сна"""
    dream = Dream.query.get_or_404(dream_id)
    if dream.user_id != current_user.user_id:
        flash('У вас нет доступа к этому сну', 'danger')
        return redirect(url_for('dreams.index'))
    
    # Получаем временную сгенерированную картинку из сессии
    temp_generated_image = session.pop('temp_generated_image', None)

    if request.method == 'POST':
        dream.title = request.form.get('title')
        dream.content = request.form.get('content')
        dream.dream_date = datetime.strptime(request.form.get('dream_date'), '%Y-%m-%d').date()
        dream.mood = request.form.get('mood', type=int)
        dream.updated_at = datetime.now()
        
        generated_image_url = request.form.get('generated_image_url')
        user_image_file = request.files.get('user_image')
        
        # Приоритет: загруженная пользователем картинка > сгенерированная
        if user_image_file and user_image_file.filename:
            filename = save_file(user_image_file, current_app.config['DREAM_IMAGES_FOLDER'])
            if filename:
                # Удаляем старую картинку пользователя, если есть
                if dream.user_image:
                    db.session.delete(dream.user_image)
                user_image = UserImage(
                    dream_id=dream.dream_id,
                    user_id=current_user.user_id,
                    image_url=f'/uploads/dream_images/{filename}'
                )
                db.session.add(user_image)
        elif generated_image_url or temp_generated_image:
            final_url = generated_image_url or temp_generated_image
            if dream.generated_image:
                dream.generated_image.image_url = final_url
            else:
                gen_image = GeneratedImage(
                    dream_id=dream.dream_id,
                    image_url=final_url
                )
                db.session.add(gen_image)
        
        db.session.commit()
        flash('Сон успешно обновлён!', 'success')
        return redirect(url_for('dreams.show', dream_id=dream.dream_id))

    return render_template('dreams/form.html', dream=dream, temp_generated_image=temp_generated_image)


@bp.route('/<int:dream_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(dream_id):
    """Удаление сна"""
    dream = Dream.query.get_or_404(dream_id)
    if dream.user_id != current_user.user_id:
        flash('У вас нет доступа к этому сну', 'danger')
        return redirect(url_for('dreams.index'))

    db.session.delete(dream)
    db.session.commit()
    flash('Сон удалён', 'success')
    return redirect(url_for('dreams.index'))


@bp.route('/stats')
@login_required
def stats():
    """JSON статистика для профиля"""
    from sqlalchemy import func
    
    dream_count = Dream.query.filter_by(user_id=current_user.user_id).count()
    avg_mood = db.session.query(func.avg(Dream.mood)).filter_by(user_id=current_user.user_id).scalar()
    top_symbol = None
    
    return {
        'dream_count': dream_count,
        'avg_mood': float(avg_mood) if avg_mood else None,
        'top_symbol': top_symbol
    }


@bp.route('/generate_image', methods=['POST'])
@login_required
def generate_image():
    """Генерация картинки по тексту сна"""
    data = request.get_json()
    content = data.get('content', '')
    
    if not content:
        return {'success': False, 'error': 'Нет текста для генерации'}, 400
    
    prompt = content[:200]
    image_url = generate_ai_image(prompt)
    
    if image_url:
        # Сохраняем URL в сессии
        session['temp_generated_image'] = image_url
        return {'success': True, 'image_url': image_url}
    else:
        return {'success': False, 'error': 'Не удалось сгенерировать картинку'}, 500


@bp.route('/regenerate_image/<int:dream_id>', methods=['POST'])
@login_required
def regenerate_image(dream_id):
    """Регенерация картинки для существующего сна"""
    dream = Dream.query.get_or_404(dream_id)
    if dream.user_id != current_user.user_id:
        return {'success': False, 'error': 'Нет доступа'}, 403
    
    prompt = dream.content[:200]
    image_url = generate_ai_image(prompt)
    
    if not image_url:
        return {'success': False, 'error': 'Не удалось сгенерировать картинку'}, 500
    
    # Обновляем или создаём GeneratedImage
    if dream.generated_image:
        dream.generated_image.image_url = image_url
        dream.generated_image.generated_at = datetime.now()
    else:
        gen_image = GeneratedImage(
            dream_id=dream.dream_id,
            image_url=image_url
        )
        db.session.add(gen_image)
    
    db.session.commit()
    return {'success': True}

