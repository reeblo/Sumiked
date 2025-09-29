from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'sumiked_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/img/products'

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
            role TEXT DEFAULT 'admin'
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insertar usuario admin por defecto (contraseña: admin123)
    try:
        cursor.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            ('admin', generate_password_hash('admin123'), 'admin')
        )
    except sqlite3.IntegrityError:
        pass  # El usuario ya existe
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('sumiked.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicializar base de datos al iniciar
init_db()

# Middleware para verificar autenticación en rutas protegidas
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas principales existentes
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
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('productos.html', products=products)

@app.route('/graciasati')
def graciasati():
    return render_template('graciasati.html')

# Sistema de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('index'))

# Panel de administración
@app.route('/admin')
@login_required
def admin():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin.html', products=products)

# API para productos
@app.route('/api/products', methods=['GET', 'POST'])
@login_required
def api_products():
    if request.method == 'GET':
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM products').fetchall()
        conn.close()
        return jsonify([dict(product) for product in products])
    
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        category = data.get('category')
        stock = data.get('stock', 0)
        image_url = data.get('image_url', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO products (name, description, price, category, stock, image_url) VALUES (?, ?, ?, ?, ?, ?)',
            (name, description, price, category, stock, image_url)
        )
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'product_id': product_id})

@app.route('/api/products/<int:product_id>', methods=['PUT', 'DELETE'])
@login_required
def api_product_detail(product_id):
    conn = get_db_connection()
    
    if request.method == 'PUT':
        data = request.get_json()
        conn.execute(
            'UPDATE products SET name=?, description=?, price=?, category=?, stock=?, image_url=? WHERE id=?',
            (data.get('name'), data.get('description'), data.get('price'), 
             data.get('category'), data.get('stock'), data.get('image_url'), product_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        conn.execute('DELETE FROM products WHERE id=?', (product_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    # ... después de las otras rutas en app.py

# Rutas para incluir navbar y footer
@app.route('/navbar')
def navbar():
    return render_template('navbar.html')

@app.route('/footer')
def footer():
    return render_template('footer.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)