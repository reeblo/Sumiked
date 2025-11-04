from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.middleware.auth import login_required, admin_required
from app.models import Product, User
from app.services.security_service import SecurityService
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard principal del admin"""
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    recent_logs = SecurityService.get_recent_logs(limit=10)
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         active_products=active_products,
                         total_users=total_users,
                         recent_logs=recent_logs)

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    """Lista de productos"""
    products = Product.query.all()
    return render_template('admin/admin_products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    """Agregar nuevo producto"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        category = request.form.get('category')
        stock = int(request.form.get('stock', 0))
        
        # Manejar imagen
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join('static/img/products', filename))
                image_url = f'img/products/{filename}'
        
        product = Product(
            name=name,
            description=description,
            price=price,
            category=category,
            stock=stock,
            image_url=image_url
        )
        product.save()
        
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/add_product.html')

@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    """Editar producto"""
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price', 0))
        product.category = request.form.get('category')
        product.stock = int(request.form.get('stock', 0))
        
        # Manejar imagen
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join('static/img/products', filename))
                product.image_url = f'img/products/{filename}'
        
        product.save()
        
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/edit_product.html', product=product)

@admin_bp.route('/products/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    """Eliminar producto"""
    product = Product.query.get_or_404(id)
    product.delete()
    
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Gestionar usuarios"""
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'admin')
        
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'error')
            return render_template('admin/create_user.html')
        
        user = User(username=username, role=role)
        user.set_password(password)
        user.save()
        
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/create_user.html')