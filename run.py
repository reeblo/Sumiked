#!/usr/bin/env python3
"""
Punto de entrada principal para Sumiked
"""
import os
from app import create_app
from init_database import init_database
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = create_app()

if __name__ == '__main__':
    # Inicializar base de datos si no existe
    with app.app_context():
        init_database()
    
    # Configuración del servidor
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Iniciando Sumiked en http://{host}:{port}")
    print(f"📊 Entorno: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🐛 Debug: {debug}")
    
    app.run(host=host, port=port, debug=debug)