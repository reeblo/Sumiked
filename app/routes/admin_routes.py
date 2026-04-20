from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.middleware.auth import login_required, admin_required
from app.models import Product, User
from app.services.security_service import SecurityService
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__)

# Registrar con el endpoint por defecto (nombre de la función -> 'dashboard'),
# así url_for('admin.dashboard') funcionará correctamente.
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard principal del admin"""
    try:
        # Obtener estadísticas
        total_products = Product.query.count()
        total_users = User.query.count()
        
        # Productos con stock bajo (menos de 5)
        low_stock = Product.query.filter(Product.stock < 5, Product.stock > 0).count()
        
        # Productos agotados
        out_of_stock = Product.query.filter_by(stock=0).count()
        
        # Productos recientes (últimos 5)
        recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
        
        # Logs recientes (con manejo de errores)
        try:
            recent_logs = SecurityService().get_recent_logs(limit=10)
        except Exception as e:
            print(f"Error al obtener logs: {str(e)}")
            recent_logs = []
        
        # ✅ CORRECCIÓN: Usar 'admin/admin.html' en lugar de 'admin/dashboard.html'
        return render_template('admin/admin.html',
                            total_products=total_products,
                            total_users=total_users,
                            low_stock=low_stock,
                            out_of_stock=out_of_stock,
                            recent_products=recent_products,
                            recent_logs=recent_logs)
    except Exception as e:
        # manejar/loggear excepción
        print("Error en admin.dashboard:", e)
        recent_products = []
        low_stock = out_of_stock = total_products = total_users = 0
        flash(f'Error al cargar el dashboard: {str(e)}', 'error')
        return render_template('admin/admin.html',
                            total_products=total_products,
                            total_users=total_users,
                            low_stock=low_stock,
                            out_of_stock=out_of_stock,
                            recent_products=recent_products,
                            recent_logs=recent_logs)

@admin_bp.route('/products')
@login_required
@admin_required
def admin_products():  
    """Lista de productos"""
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/admin_products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    """Agregar nuevo producto"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = float(request.form.get('price', 0))
            category = request.form.get('category', '')
            stock = int(request.form.get('stock', 0))
            image_url = request.form.get('image_url', '').strip()
            
            # Validaciones básicas
            if not name or not category:
                flash('Nombre y categoría son requeridos', 'error')
                return render_template('admin/add_product.html')
            
            if price < 0 or stock < 0:
                flash('Precio y stock no pueden ser negativos', 'error')
                return render_template('admin/add_product.html')
            
            # ✅ NUEVA: Validar longitud de URL
            if image_url and len(image_url) > 500:
                flash('La URL de la imagen es demasiado larga (máximo 500 caracteres). Usa un acortador de URLs o sube la imagen a un servicio como ImgBB.', 'error')
                return render_template('admin/add_product.html')
            
            # ✅ NUEVA: Validar formato de URL
            if image_url and not (image_url.startswith('http://') or image_url.startswith('https://')):
                flash('La URL de la imagen debe comenzar con http:// o https://', 'error')
                return render_template('admin/add_product.html')
            
            # Crear producto
            product = Product(
                name=name,
                description=description if description else None,
                price=price,
                category=category,
                stock=stock,
                image_url=image_url if image_url else None,
                is_active=True
            )
            product.save()
            
            # Log de seguridad
            SecurityService().log_action('producto_creado', session.get('user_id'))
            
            flash('Producto agregado exitosamente', 'success')
            return redirect(url_for('admin.admin_products'))
            
        except ValueError as e:
            flash('Error en los datos ingresados. Verifica que el precio sea un número válido.', 'error')
            return render_template('admin/add_product.html')
        except Exception as e:
            flash(f'Error al crear producto: {str(e)}', 'error')
            return render_template('admin/add_product.html')
    
    return render_template('admin/add_product.html')

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):  # ✅ Nombre de parámetro consistente
    """Editar producto"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            product.name = request.form.get('name', '').strip()
            product.description = request.form.get('description', '').strip()
            product.price = float(request.form.get('price', 0))
            product.category = request.form.get('category', '')
            product.stock = int(request.form.get('stock', 0))
            image_url = request.form.get('image_url', '').strip()
            
            # Validaciones
            if not product.name or not product.category:
                flash('Nombre y categoría son requeridos', 'error')
                return render_template('admin/edit_product.html', product=product)
            
            if product.price < 0 or product.stock < 0:
                flash('Precio y stock no pueden ser negativos', 'error')
                return render_template('admin/edit_product.html', product=product)
            
            # ✅ Validar longitud de URL
            if image_url and len(image_url) > 500:
                flash('La URL de la imagen es demasiado larga (máximo 500 caracteres). Por favor, usa un servicio de acortamiento de URLs.', 'error')
                return render_template('admin/edit_product.html', product=product)
            
            # Validar formato de URL
            if image_url and not (image_url.startswith('http://') or image_url.startswith('https://')):
                flash('La URL de la imagen debe comenzar con http:// o https://', 'error')
                return render_template('admin/edit_product.html', product=product)
            
            product.image_url = image_url if image_url else None
            product.save()
            
            SecurityService().log_action('producto_editado', session.get('user_id'))
            
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('admin.admin_products'))
            
        except ValueError:
            flash('Error en los datos ingresados. Verifica que el precio sea un número válido.', 'error')
            return render_template('admin/edit_product.html', product=product)
        except Exception as e:
            flash(f'Error al actualizar producto: {str(e)}', 'error')
            return render_template('admin/edit_product.html', product=product)
    
    return render_template('admin/edit_product.html', product=product)

@admin_bp.route('/products/delete/<int:product_id>')
@login_required
@admin_required
def delete_product(product_id):  # ✅ Cambiado a GET para coincidir con el template
    """Eliminar producto"""
    try:
        product = Product.query.get_or_404(product_id)
        product_name = product.name
        product.delete()
        
        SecurityService().log_action('producto_eliminado', session.get('user_id'))
        
        flash(f'Producto "{product_name}" eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar producto: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin_products'))

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Gestionar usuarios"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            role = request.form.get('role', 'admin')
            
            # Validaciones
            if not username or not password:
                flash('Usuario y contraseña son requeridos', 'error')
                return render_template('admin/create_user.html')
            
            if password != confirm_password:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('admin/create_user.html')
            
            if len(password) < 8:
                flash('La contraseña debe tener al menos 8 caracteres', 'error')
                return render_template('admin/create_user.html')
            
            if User.query.filter_by(username=username).first():
                flash('El usuario ya existe', 'error')
                return render_template('admin/create_user.html')
            
            # Crear usuario
            user = User(username=username, role=role, is_active=True)
            user.set_password(password)
            user.save()
            
            SecurityService().log_action('usuario_creado', session.get('user_id'))
            
            flash(f'Usuario "{username}" creado exitosamente', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            flash(f'Error al crear usuario: {str(e)}', 'error')
            return render_template('admin/create_user.html')
    
    return render_template('admin/create_user.html')