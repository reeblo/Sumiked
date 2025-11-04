from flask import Blueprint, render_template
from app.models import Product

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@public_bp.route('/about')
def about():
    """Página acerca de"""
    return render_template('about.html')

@public_bp.route('/servicios')
def servicios():
    """Página de servicios"""
    return render_template('servicios.html')

@public_bp.route('/productos')
def productos():
    """Página de productos"""
    products = Product.query.filter_by(is_active=True).all()
    return render_template('productos.html', products=products)

@public_bp.route('/graciasati')
def graciasati():
    """Página de agradecimiento"""
    return render_template('graciasati.html')