from flask import Flask
from flask_cors import CORS
from app.extensions import db, bcrypt, jwt, migrate
from app.routes.auth_routes import auth_blueprint
from app.routes.main_routes import main_blueprint
from app.config import Config

def create_app():
    poultry_app = Flask(__name__)
    CORS(poultry_app)
    poultry_app.config.from_object(Config)

    # Initialize extensions
    db.init_app(poultry_app)
    bcrypt.init_app(poultry_app)
    jwt.init_app(poultry_app)
    migrate.init_app(poultry_app,db)

    # Register blueprints
    poultry_app.register_blueprint(auth_blueprint)
    poultry_app.register_blueprint(main_blueprint)

    return poultry_app
