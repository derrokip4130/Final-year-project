import uuid
from app import db
from datetime import datetime
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB

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

disease_symptom = db.Table(
    'disease_symptom',
    db.Column('disease_id', db.String(10), db.ForeignKey('diseases.disease_id'), primary_key=True),
    db.Column('symptom_id', db.String(10), db.ForeignKey('symptom.symptom_id'), primary_key=True)
)

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


class Disease(db.Model):
    __tablename__ = 'diseases'

    disease_id = db.Column(db.String(10), primary_key=True)
    disease_name = db.Column(db.String(50), nullable=False)
    disease_description = db.Column(db.String(100), nullable=True)
    causes = db.Column(db.String(255), nullable=True)  # Causes of the disease
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    symptoms = db.relationship('Symptom', secondary=disease_symptom, backref=db.backref('diseases', lazy='dynamic'))

    def __repr__(self):
        return self.disease_name

    @staticmethod
    def generate_disease_id():
        last_disease = Disease.query.order_by(Disease.disease_id.desc()).first()
        if last_disease:
            last_id = int(last_disease.disease_id.split('-')[1])  # Extract numeric part
            new_id = f"D-{last_id + 1:03d}"  # Increment and format as D-XXX
        else:
            new_id = "D-001"  # First entry
        
        return new_id

class Breed(db.Model):

    breed_id = db.Column(db.String(5), primary_key=True)
    breed_name = db.Column(db.String(50))
    breed_characteristics = db.Column(JSONB)
    breed_purpose = db.Column(db.String(10))
    breed_category = db.Column(db.String(10))
    feeding_nutrition = db.Column(JSONB)
    housing_environment = db.Column(JSONB)
    disease_prevention_health = db.Column(JSONB)
    breeding_reproduction = db.Column(JSONB)
    productivity_economics = db.Column(JSONB)

    def __repr__(self):
        return self.breed_name

    @staticmethod
    def generate_breed_id():
        last_breed = Breed.query.order_by(Breed.breed_id.desc()).first()
        if last_breed:
            last_id = int(last_breed.breed_id.split('-')[1])  # Extract numeric part
            new_id = f"B-{last_id + 1:03d}"  # Increment and format as D-XXX
        else:
            new_id = "B-001"  # First entry
        
        return new_id
