def register_commands(app):
    """Registra comandos personalizados de Flask en la aplicación."""
    
    @app.cli.command("init-db")
    def init_db():
        """Inicializa la base de datos."""
        from app.models import db
        db.create_all()
        print("✅ Base de datos inicializada correctamente.")
    
    @app.cli.command("seed-db")
    def seed_db():
        """Llena la base de datos con datos iniciales."""
        # Aquí puedes importar tus modelos y agregar registros de ejemplo
        print("🌱 Base de datos sembrada con datos de prueba.")
