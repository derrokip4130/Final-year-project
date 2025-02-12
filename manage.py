from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)  # Initialize Flask-Migrate

if __name__ == "__main__":
    app.run()
