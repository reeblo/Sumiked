from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
import os
import os

# Inicializar extensiones principales
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    app.secret_key = app.config.get('SECRET_KEY') or 'dev-secret-change-me'  # asegurar sesiones en dev
    db.init_app(app)
    migrate.init_app(app, db)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from app.routes.public_routes import public_bp
    from app.routes.auth_routes import auth_bp, logout as logout_view
    from app.routes.admin_routes import admin_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    # DEBUG: mostrar rutas registradas para verificar endpoints
    from pprint import pprint
    print("=== URL MAP ===")
    pprint(sorted(f"{rule.rule} -> {rule.endpoint}" for rule in app.url_map.iter_rules()))

    app.add_url_rule('/logout', endpoint='logout', view_func=logout_view)

    from app.utils.commands import register_commands
    register_commands(app)

    # tener en cuenta para que Flask-Migrate detecte modelos
    from app import models
  
    return app
