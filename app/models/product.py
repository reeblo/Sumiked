from app import db
from app.models.base import BaseModel

class Product(BaseModel):
    __tablename__ = 'products'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255))
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def to_dict(self):
        """Convertir a diccionario"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'category': self.category,
            'image_url': self.image_url,
            'stock': self.stock,
            'is_active': self.is_active
        })
        return data
    
    def __repr__(self):
        return f'<Product {self.name}>'