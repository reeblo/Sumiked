from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión como administrador.', 'warning')
            return redirect(url_for('auth.login'))
        # Verifica si el rol del usuario en sesión es 'admin'
        if session.get('role') != 'admin':
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('public.home'))  # Ajusta al nombre de tu vista pública
        return f(*args, **kwargs)
    return decorated_function
