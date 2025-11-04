"""
Script para inicializar la base de datos
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializar la base de datos con tablas y usuario admin"""
    
    db_path = 'sumiked.db'
    db_exists = os.path.exists(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT,
            stock INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de logs de seguridad
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Verificar si existe usuario admin
    admin_exists = cursor.execute(
        'SELECT COUNT(*) FROM users WHERE role = "admin" AND is_active = 1'
    ).fetchone()[0]
    
    # Crear usuario admin si no existe
    if admin_exists == 0:
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        temp_password = "Admin123!"  # Contraseña temporal
        hashed_password = generate_password_hash(temp_password)
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hashed_password, 'admin')
            )
            
            print("=" * 60)
            print("🔐 CREDENCIALES TEMPORALES PARA SUMIKED:")
            print("=" * 60)
            print(f"👤 USUARIO: {username}")
            print(f"🔑 CONTRASEÑA: {temp_password}")
            print("=" * 60)
            print("⚠️  ¡IMPORTANTE!")
            print("• Después de iniciar sesión, CAMBIA la contraseña")
            print("• En el panel admin ve a: Usuarios → Cambiar Contraseña")
            print("• Esta contraseña es temporal e insegura")
            print("=" * 60)
            
        except sqlite3.IntegrityError:
            print("ℹ️  El usuario admin ya existe en la base de datos")
    else:
        print("✅ Base de datos inicializada - Usuario admin existe")
    
    conn.commit()
    conn.close()
    
    if not db_exists:
        print("🗃️  Base de datos creada exitosamente")
    else:
        print("🗃️  Base de datos verificada")

if __name__ == '__main__':
    init_database()