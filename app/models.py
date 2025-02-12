import uuid
from app import db
from datetime import datetime
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    ADMIN = "admin"
    FARMER = "farmer"

    user_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone_num = db.Column(db.String(10), unique=True, nullable=True)
    user_role = db.Column(db.String(30), nullable=False, default=FARMER)  # Default to farmer
    location = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<User {self.username} - Role: {self.user_role}>"
    
    def check_password(self, password):
        """Checks if the provided password matches the stored hash"""
        return check_password_hash(self.password, password)
    
    def get_id(self):
        return str(self.user_id)
    
    @property
    def is_admin(self):
        """Check if the user is an admin"""
        return self.user_role == self.ADMIN

    @property
    def is_farmer(self):
        """Check if the user is a farmer"""
        return self.user_role == self.FARMER

class Symptom(db.Model):
    symptom_id = db.Column(db.String(10), primary_key=True)
    symptom_name = db.Column(db.String(50), nullable=False)
    symptom_description = db.Column(db.String(100), nullable = True)

    def __repr__(self):
        return self.symptom_name

    @staticmethod
    def generate_symptom_id():
        last_symptom = Symptom.query.order_by(Symptom.symptom_id.desc()).first()
        if last_symptom:
            last_id = int(last_symptom.symptom_id.split('-')[1])  # Extract numeric part
            new_id = f"S-{last_id + 1:03d}"  # Increment and format as S-XXX
        else:
            new_id = "S-001"  # First entry
        
        return new_id

    def __init__(self, name):
        self.symptom_id = self.generate_symptom_id()
        self.name = name
