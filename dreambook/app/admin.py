from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Symbol
from app.auth import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')


#управление пользователми

@bp.route('/users')
@login_required
@admin_required
def users():
    """Список всех пользователей"""
    users_list = User.query.order_by(User.user_id).all()
    return render_template('admin/users.html', users=users_list)


@bp.route('/users/<int:user_id>/toggle_role', methods=['POST'])
@login_required
@admin_required
def toggle_role(user_id):
    """Сменить роль пользователя (user/admin)"""
    user = User.query.get_or_404(user_id)
    if user.user_id == current_user.user_id:
        flash('Нельзя изменить свою роль', 'danger')
        return redirect(url_for('admin.users'))
    
    user.role = 'admin' if user.role == 'user' else 'user'
    db.session.commit()
    flash(f'Роль пользователя {user.username} изменена на {user.role}', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Удалить пользователя"""
    user = User.query.get_or_404(user_id)
    if user.user_id == current_user.user_id:
        flash('Нельзя удалить самого себя', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'Пользователь {user.username} удалён', 'success')
    return redirect(url_for('admin.users'))


# управление символами

@bp.route('/symbols')
@login_required
@admin_required
def symbols():
    """Список всех символов"""
    symbols_list = Symbol.query.order_by(Symbol.name).all()
    return render_template('admin/symbols.html', symbols=symbols_list)


@bp.route('/symbols/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_symbol():
    """Добавление нового символа"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        
        if not name:
            flash('Название символа не может быть пустым', 'danger')
            return redirect(url_for('admin.new_symbol'))
        
        if Symbol.query.filter_by(name=name).first():
            flash(f'Символ "{name}" уже существует', 'danger')
            return redirect(url_for('admin.new_symbol'))
        
        symbol = Symbol(name=name)
        db.session.add(symbol)
        db.session.commit()
        flash(f'Символ "{name}" добавлен', 'success')
        return redirect(url_for('admin.symbols'))
    
    return render_template('admin/symbol_form.html', symbol=None)


@bp.route('/symbols/<int:symbol_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_symbol(symbol_id):
    """Редактирование символа"""
    symbol = Symbol.query.get_or_404(symbol_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        
        if not name:
            flash('Название символа не может быть пустым', 'danger')
            return redirect(url_for('admin.edit_symbol', symbol_id=symbol_id))
        
        # Проверка на дубликат (исключая текущий символ)
        existing = Symbol.query.filter(Symbol.name == name, Symbol.symbol_id != symbol_id).first()
        if existing:
            flash(f'Символ "{name}" уже существует', 'danger')
            return redirect(url_for('admin.edit_symbol', symbol_id=symbol_id))
        
        symbol.name = name
        db.session.commit()
        flash(f'Символ переименован в "{name}"', 'success')
        return redirect(url_for('admin.symbols'))
    
    return render_template('admin/symbol_form.html', symbol=symbol)


@bp.route('/symbols/<int:symbol_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_symbol(symbol_id):
    """Удаление символа"""
    symbol = Symbol.query.get_or_404(symbol_id)
    name = symbol.name
    db.session.delete(symbol)
    db.session.commit()
    flash(f'Символ "{name}" удалён', 'success')
    return redirect(url_for('admin.symbols'))