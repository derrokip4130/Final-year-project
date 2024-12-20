import secrets
from app import db
from flask_sqlalchemy import SQLAlchemy

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=False)
    phone_num = db.Column(db.String(10), unique=True, nullable=True)
    token = db.Column(db.String(200), unique=True, nullable=True)

    def __repr__(self):
        return f"<User {self.name}>"

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(64)  # Generate a random token
