from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
import os
import os

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from app.routes.public_routes import public_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.utils.commands import register_commands
    register_commands(app)

    # 👇 IMPORTANTE para que Flask-Migrate detecte modelos
    from app import models

    return app
