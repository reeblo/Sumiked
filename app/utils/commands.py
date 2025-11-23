import click
from app import db
from app.models import User

def register_commands(app):

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("password")
    def create_admin(username, password):
        """Crear un usuario administrador"""
        if User.query.filter_by(username=username).first():
            click.echo("❌ El usuario ya existe")
            return

        admin = User(username=username, role="admin")
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        click.echo("✅ Administrador creado correctamente")
