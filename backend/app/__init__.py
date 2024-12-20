from flask import Flask
from flask_cors import CORS
from app.extensions import db, bcrypt, jwt, migrate
from app.routes.auth_routes import auth_blueprint
from app.routes.main_routes import main_blueprint
from app.config import Config

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app,db)

    # Register blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    return app
