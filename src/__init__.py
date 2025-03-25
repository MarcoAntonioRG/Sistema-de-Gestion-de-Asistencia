from flask import Flask
from flask_session import Session
from flask_migrate import Migrate
from .config import Config
from .routes import register_routes
from .extensions import db
from src.models import *


def create_app():
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates",
    )
    app.config.from_object(Config)

    # Inicializar Flask-Session
    Session(app)

    db.init_app(app)  # Inicializa la base de datos con la aplicación Flask
    migrate = Migrate(
        app, db
    )  # Maneja las migraciones de la base de datos (para modificar la estructura de las tablas)

    # Inicializar y registrar rutas
    register_routes(app)

    return app
