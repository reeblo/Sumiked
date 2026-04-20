from app.models.security_log import SecurityLog
from flask import request
from datetime import datetime, timedelta

class SecurityService:
    """Servicio para manejar la seguridad y auditoría del sistema"""
    
    @staticmethod
    def log_action(action, user_id=None, details=None):
        """
        Registrar una acción de seguridad
        
        Args:
            action (str): Tipo de acción realizada
            user_id (int, optional): ID del usuario que realizó la acción
            details (str, optional): Detalles adicionales
        
        Returns:
            SecurityLog: El log creado
        """
        try:
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            log = SecurityLog.log_action(
                action=action,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details
            )
            return log
        except Exception as e:
            print(f"Error al crear log de seguridad: {str(e)}")
            return None
    
    @staticmethod
    def get_recent_logs(limit=10):
        """
        Obtener logs recientes
        
        Args:
            limit (int): Número máximo de logs a retornar
        
        Returns:
            list: Lista de logs recientes
        """
        try:
            return SecurityLog.get_recent(limit=limit)
        except Exception as e:
            print(f"Error al obtener logs recientes: {str(e)}")
            return []
    
    @staticmethod
    def get_user_logs(user_id, limit=None):
        """
        Obtener logs de un usuario específico
        
        Args:
            user_id (int): ID del usuario
            limit (int, optional): Número máximo de logs
        
        Returns:
            list: Lista de logs del usuario
        """
        try:
            return SecurityLog.get_by_user(user_id=user_id, limit=limit)
        except Exception as e:
            print(f"Error al obtener logs de usuario: {str(e)}")
            return []
    
    @staticmethod
    def get_failed_login_attempts(ip_address, minutes=15):
        """
        Contar intentos fallidos de login desde una IP en un período de tiempo
        
        Args:
            ip_address (str): Dirección IP a verificar
            minutes (int): Minutos hacia atrás a considerar
        
        Returns:
            int: Número de intentos fallidos
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
            logs = SecurityLog.query.filter(
                SecurityLog.action == 'login_fallido',
                SecurityLog.ip_address == ip_address,
                SecurityLog.created_at >= time_threshold
            ).all()
            return len(logs)
        except Exception as e:
            print(f"Error al contar intentos fallidos: {str(e)}")
            return 0
    
    @staticmethod
    def is_ip_blocked(ip_address, max_attempts=5, minutes=15):
        """
        Verificar si una IP está bloqueada por exceso de intentos fallidos
        
        Args:
            ip_address (str): Dirección IP a verificar
            max_attempts (int): Número máximo de intentos permitidos
            minutes (int): Período de tiempo a considerar
        
        Returns:
            bool: True si la IP está bloqueada
        """
        attempts = SecurityService.get_failed_login_attempts(ip_address, minutes)
        return attempts >= max_attempts
    
    @staticmethod
    def get_activity_summary(days=7):
        """
        Obtener un resumen de actividad del sistema
        
        Args:
            days (int): Número de días hacia atrás
        
        Returns:
            dict: Resumen de actividad
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(days=days)
            logs = SecurityLog.query.filter(
                SecurityLog.created_at >= time_threshold
            ).all()
            
            summary = {
                'total_actions': len(logs),
                'login_exitoso': 0,
                'login_fallido': 0,
                'logout': 0,
                'cambio_contrasena': 0,
                'producto_creado': 0,
                'producto_editado': 0,
                'producto_eliminado': 0,
                'usuario_creado': 0
            }
            
            for log in logs:
                if log.action in summary:
                    summary[log.action] += 1
            
            return summary
        except Exception as e:
            print(f"Error al obtener resumen de actividad: {str(e)}")
            return {
                'total_actions': 0,
                'login_exitoso': 0,
                'login_fallido': 0
            }