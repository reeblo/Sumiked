from flask import request
from app import db
from app.models import SecurityLog

class SecurityService:
    """Servicio para manejo de seguridad y logs"""
    
    @staticmethod
    def log_action(action, user_id=None):
        """Registrar acción de seguridad"""
        try:
            log = SecurityLog(
                user_id=user_id,
                action=action,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            log.save()
        except Exception as e:
            print(f"Error al registrar log de seguridad: {str(e)}")
    
    @staticmethod
    def get_recent_logs(limit=50):
        """Obtener logs recientes"""
        return SecurityLog.query.order_by(SecurityLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_user_logs(user_id, limit=20):
        """Obtener logs de un usuario específico"""
        return SecurityLog.query.filter_by(user_id=user_id)\
            .order_by(SecurityLog.created_at.desc())\
            .limit(limit).all()