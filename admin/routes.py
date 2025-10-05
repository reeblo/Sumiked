from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash  # FALTABA ESTA IMPORTACIÓN

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

def get_db_connection():
    conn = sqlite3.connect('sumiked.db')
    conn.row_factory = sqlite3.Row
    return conn


def log_security_action(action, user_id=None):
    from flask import request
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO security_logs (user_id, action, ip_address, user_agent) VALUES (?, ?, ?, ?)',
        (user_id, action, request.remote_addr, request.headers.get('User-Agent'))
    )
    conn.commit()
    conn.close()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            log_security_action('intento_acceso_admin_sin_permisos', session.get('user_id'))
            flash('Acceso denegado. Se requieren privilegios de administrador.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    
    # Estadísticas actualizadas
    total_products = conn.execute('SELECT COUNT(*) FROM products WHERE is_active = 1').fetchone()[0]
    total_users = conn.execute('SELECT COUNT(*) FROM users WHERE is_active = 1').fetchone()[0]
    
    # Productos con stock bajo y agotados
    low_stock = conn.execute('SELECT COUNT(*) FROM products WHERE stock < 5 AND stock > 0').fetchone()[0]
    out_of_stock = conn.execute('SELECT COUNT(*) FROM products WHERE stock = 0').fetchone()[0]
    
    # Productos recientes
    recent_products = conn.execute(
        'SELECT * FROM products WHERE is_active = 1 ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    
    # Logs de seguridad
    recent_logs = conn.execute(
        'SELECT * FROM security_logs ORDER BY timestamp DESC LIMIT 10'
    ).fetchall()
    
    conn.close()
    
    return render_template('admin.html',
                        total_products=total_products,
                        total_users=total_users,
                        low_stock=low_stock,
                        out_of_stock=out_of_stock,
                        recent_products=recent_products,
                        recent_logs=recent_logs)

# Gestión de usuarios
@admin_bp.route('/users')
@admin_required
def manage_users():
    """Gestionar usuarios"""
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, role, is_active, created_at, last_login FROM users').fetchall()
    conn.close()
    return render_template('manage_users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Crear nuevos usuarios de forma segura"""
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        
        # Validaciones de seguridad
        if len(username) < 3:
            flash('El usuario debe tener al menos 3 caracteres', 'error')
            return render_template('create_user.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('create_user.html')
        
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'error')
            return render_template('create_user.html')
        
        # Verificar fortaleza de contraseña
        if not any(char.isdigit() for char in password):
            flash('La contraseña debe contener al menos un número', 'error')
            return render_template('create_user.html')
        
        if not any(char.isupper() for char in password):
            flash('La contraseña debe contener al menos una mayúscula', 'error')
            return render_template('create_user.html')
        
        conn = get_db_connection()
        
        # Verificar si el usuario ya existe
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if existing_user:
            conn.close()
            flash('El usuario ya existe', 'error')
            return render_template('create_user.html')
        
        # Crear usuario
        conn.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            (username, generate_password_hash(password), role)
        )
        conn.commit()
        conn.close()
        
        log_security_action(f'usuario_creado: {username}', session['user_id'])
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('create_user.html')

# Gestión de productos (código existente se mantiene igual)
@admin_bp.route('/products')
@admin_required
def admin_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        stock = int(request.form['stock'])
        image_url = request.form.get('image_url', '')
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO products (name, description, price, category, stock, image_url) VALUES (?, ?, ?, ?, ?, ?)',
            (name, description, price, category, stock, image_url)
        )
        conn.commit()
        conn.close()
        
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('admin.admin_products'))
    
    return render_template('add_product.html')

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        stock = int(request.form['stock'])
        image_url = request.form.get('image_url', '')
        
        conn.execute(
            'UPDATE products SET name=?, description=?, price=?, category=?, stock=?, image_url=? WHERE id=?',
            (name, description, price, category, stock, image_url, product_id)
        )
        conn.commit()
        conn.close()
        
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('admin.admin_products'))
    
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    
    if product is None:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('admin.admin_products'))
    
    return render_template('edit_product.html', product=product)

@admin_bp.route('/products/delete/<int:product_id>')
@admin_required
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('admin.admin_products'))

# API para productos (AJAX)
@admin_bp.route('/api/products', methods=['GET', 'POST'])
@admin_required
def api_products():
    conn = get_db_connection()
    
    if request.method == 'GET':
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
        
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO products (name, description, price, category, stock, image_url) VALUES (?, ?, ?, ?, ?, ?)',
            (name, description, price, category, stock, image_url)
        )
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'product_id': product_id})

@admin_bp.route('/api/products/<int:product_id>', methods=['PUT', 'DELETE'])
@admin_required
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