"""
Punto de ejecucion Sumiked.
"""
import os
from app import create_app
from dotenv import load_dotenv

# Carga variables de entorno desde el archivo .env
load_dotenv()

app = create_app()

if __name__ == '__main__':
    # configuracion del host y puerto desde variables de entorno
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Iniciando Sumiked en http://{host}:{port}")
    print(f"📊 Entorno: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🐛 Debug: {debug}")
    
    app.run(host=host, port=port, debug=debug)