from flask import Flask, render_template
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

    from flask import render_template

    @app.errorhandler(404)
    @app.errorhandler(500)
    @app.errorhandler(403)
    @app.errorhandler(400)
    @app.errorhandler(401)
    def handle_errors(error):
        return render_template('error.html', error_code=error.code, error_message=error.description), error.code

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
