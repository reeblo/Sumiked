#!/usr/bin/env python3
"""
Verificador de instalación y configuración
"""
import os
import sys
import sqlite3
from pathlib import Path

def check_setup():
    """Verificar que todo esté configurado correctamente"""
    print("🔍 Verificando instalación de Sumiked...")
    
    issues = []
    
    # 1. Verificar archivo .env
    if not Path('.env').exists():
        issues.append("❌ Archivo .env no encontrado. Copia .env.example a .env")
    
    # 2. Verificar variables de entorno críticas
    required_env_vars = ['SECRET_KEY', 'DATABASE_URL']
    for var in required_env_vars:
        if not os.environ.get(var):
            issues.append(f"❌ Variable de entorno {var} no configurada")
    
    # 3. Verificar base de datos
    try:
        conn = sqlite3.connect('sumiked.db')
        cursor = conn.cursor()
        
        # Verificar tablas
        tables = ['users', 'products', 'security_logs']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cursor.fetchone():
                issues.append(f"❌ Tabla {table} no existe en la base de datos")
        
        # Verificar usuario admin
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin" AND is_active = 1')
        if cursor.fetchone()[0] == 0:
            issues.append("❌ No hay usuario admin en la base de datos")
        
        conn.close()
    except Exception as e:
        issues.append(f"❌ Error al verificar base de datos: {e}")
    
    # 4. Verificar estructura de directorios
    required_dirs = ['static/img/products', 'templates/admin', 'logs']
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            issues.append(f"❌ Directorio {dir_path} no existe")
    
    # Mostrar resultados
    if issues:
        print("\n⚠️  Se encontraron problemas:")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n🔧 Problemas encontrados: {len(issues)}")
        return False
    else:
        print("✅ Todas las verificaciones pasaron correctamente")
        return True

if __name__ == '__main__':
    success = check_setup()
    sys.exit(0 if success else 1)