from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import User
from app.services.security_service import SecurityService
from app.middleware.auth import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    # Si ya está autenticado, redirigir al admin
    if 'user_id' in session:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validaciones básicas
        if not username or not password:
            flash('Usuario y contraseña son requeridos', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and user.check_password(password):
            # Autenticación exitosa
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session.permanent = True
            
            # Actualizar último login
            user.update_last_login()
            
            SecurityService.log_action('login_exitoso', user.id)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            SecurityService.log_action('login_fallido')
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    user_id = session.get('user_id')
    SecurityService.log_action('logout', user_id)
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('public.index'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambiar contraseña"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if new_password != confirm_password:
            flash('Las contraseñas nuevas no coinciden', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'error')
            return render_template('change_password.html')
        
        user = User.query.get(session['user_id'])
        
        if user and user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            
            SecurityService.log_action('cambio_contrasena', session['user_id'])
            flash('Contraseña cambiada exitosamente', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Contraseña actual incorrecta', 'error')
    
    return render_template('change_password.html')