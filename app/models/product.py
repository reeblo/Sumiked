from app import db
from datetime import datetime

class Product(db.Model):
    """Modelo de Producto"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    category = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)  
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def save(self):
        """Guardar el producto en la base de datos"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """Eliminar el producto de la base de datos"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update(self, **kwargs):
        """Actualizar campos del producto"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @property
    def is_low_stock(self):
        """Verificar si el stock es bajo (menos de 5)"""
        return 0 < self.stock < 5
    
    @property
    def is_out_of_stock(self):
        """Verificar si está agotado"""
        return self.stock == 0
    
    @property
    def stock_status(self):
        """Obtener estado del stock"""
        if self.stock == 0:
            return 'agotado'
        elif self.stock < 5:
            return 'bajo'
        else:
            return 'disponible'
    
    def to_dict(self):
        """Convertir el producto a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'stock': self.stock,
            'is_active': self.is_active,
            'stock_status': self.stock_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }