from flask import Flask
from flask_cors import CORS
from app.extensions import db, bcrypt, migrate, login_manager
from app.routes.auth_routes import auth_blueprint
from app.routes.main_routes import main_blueprint
from app.config import Config
from app.models import User

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
