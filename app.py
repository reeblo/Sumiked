from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import os
import secrets
from datetime import datetime, timedelta
from admin.routes import admin_bp

app = Flask(__name__)
# Usar una clave secreta más segura
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = 'static/img/products'

# Configuración de seguridad
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # Sesión expira en 2 horas
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Cambiar a True en producción con HTTPS

# Registrar blueprint de administración
app.register_blueprint(admin_bp, url_prefix='/admin')

# Función para inicializar la base de datos
def init_db():
    """Inicializar la base de datos"""
    conn = sqlite3.connect('sumiked.db')
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT,
            stock INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de logs de seguridad
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # VERIFICAR si existe algún usuario admin
    admin_exists = cursor.execute(
        'SELECT COUNT(*) FROM users WHERE role = "admin" AND is_active = 1'
    ).fetchone()[0]
    
    # SOLO crear usuario admin si NO existe ninguno
    if admin_exists == 0:
        username = "admin"
        temp_password = "Admin123!"  # Contraseña temporal
        hashed_password = generate_password_hash(temp_password)
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hashed_password, 'admin')
            )
            
            print("=" * 60)
            print("🔐 CREDENCIALES TEMPORALES PARA SUMIKED:")
            print("=" * 60)
            print(f"👤 USUARIO: {username}")
            print(f"🔑 CONTRASEÑA: {temp_password}")
            print("=" * 60)
            print("⚠️  ¡IMPORTANTE!")
            print("• Después de iniciar sesión, CAMBIA la contraseña")
            print("• En el panel admin ve a: Usuarios → Cambiar Contraseña")
            print("• Esta contraseña es temporal e insegura")
            print("=" * 60)
            
        except sqlite3.IntegrityError:
            print("ℹ️  El usuario admin ya existe en la base de datos")
    else:
        print("✅ Base de datos inicializada - Usuario admin existe")
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('sumiked.db')
    conn.row_factory = sqlite3.Row
    return conn

def log_security_action(action, user_id=None):
    """Registrar acción de seguridad"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO security_logs (user_id, action, ip_address, user_agent) VALUES (?, ?, ?, ?)',
        (user_id, action, request.remote_addr, request.headers.get('User-Agent'))
    )
    conn.commit()
    conn.close()

# Middleware para verificar autenticación en rutas protegidas
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            log_security_action('intento_acceso_sin_autenticacion')
            flash('Por favor inicie sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        
        # Verificar que el usuario aún existe y está activo
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE id = ? AND is_active = 1', (session['user_id'],)
        ).fetchone()
        conn.close()
        
        if user is None:
            session.clear()
            log_security_action('intento_acceso_usuario_invalido', session.get('user_id'))
            flash('Sesión inválida', 'error')
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            log_security_action('intento_acceso_admin_sin_permisos', session.get('user_id'))
            flash('Acceso denegado. Se requieren privilegios de administrador.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas principales del sitio público
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

@app.route('/productos')
def productos():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products WHERE is_active = 1').fetchall()
    conn.close()
    return render_template('productos.html', products=products)

@app.route('/graciasati')
def graciasati():
    return render_template('graciasati.html')

# Sistema de autenticación mejorado
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está autenticado, redirigir al admin
    if 'user_id' in session:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        # Validaciones básicas
        if not username or not password:
            flash('Usuario y contraseña son requeridos', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND is_active = 1', (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            # Autenticación exitosa
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session.permanent = True
            
            # Actualizar último login
            conn = get_db_connection()
            conn.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user['id'],)
            )
            conn.commit()
            conn.close()
            
            log_security_action('login_exitoso', user['id'])
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            log_security_action('login_fallido')
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    log_security_action('logout', user_id)
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('index'))

# Ruta para cambiar contraseña (opcional)
@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Las contraseñas nuevas no coinciden', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'error')
            return render_template('change_password.html')
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE id = ?', (session['user_id'],)
        ).fetchone()
        
        if user and check_password_hash(user['password'], current_password):
            conn.execute(
                'UPDATE users SET password = ? WHERE id = ?',
                (generate_password_hash(new_password), session['user_id'])
            )
            conn.commit()
            conn.close()
            
            log_security_action('cambio_contrasena', session['user_id'])
            flash('Contraseña cambiada exitosamente', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            conn.close()
            flash('Contraseña actual incorrecta', 'error')
    
    return render_template('change_password.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)