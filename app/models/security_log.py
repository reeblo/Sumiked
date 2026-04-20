from app import db
from app.models.base import BaseModel

class SecurityLog(BaseModel):
    __tablename__ = 'security_logs'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    
    def to_dict(self):
        """Convertir a diccionario"""
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'action': self.action,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        })
        return data
    
    def __repr__(self):
        return f'<SecurityLog {self.action}>'