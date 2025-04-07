import uuid, pytz
from app import db
from datetime import datetime
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB

eat_tz = pytz.timezone("Africa/Nairobi")

disease_symptom = db.Table(
    'disease_symptom',
    db.Column('disease_id', db.String(10), db.ForeignKey('diseases.disease_id'), primary_key=True),
    db.Column('symptom_id', db.String(10), db.ForeignKey('symptom.symptom_id'), primary_key=True)
)

farmer_breed = db.Table(
    "farmer_breed",
    db.Column("user_id", db.String, db.ForeignKey("user.user_id"), primary_key=True),
    db.Column("breed_id", db.String(5), db.ForeignKey("breed.breed_id"), primary_key=True),
)

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

    breeds = db.relationship("Breed", secondary=farmer_breed, back_populates="farmers")
    chats = db.relationship('Chat', backref='user', lazy=True)

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


class Disease(db.Model):
    __tablename__ = 'diseases'

    disease_id = db.Column(db.String(10), primary_key=True)
    disease_name = db.Column(db.String(50), nullable=False)
    disease_description = db.Column(db.Text, nullable=True)
    disease_prevention_tips = db.Column(db.Text, nullable=True)
    causes = db.Column(db.String(255), nullable=True)  # Causes of the disease
    last_updated = db.Column(db.DateTime, default=datetime.now(eat_tz), onupdate=datetime.now(eat_tz))
    created_at = db.Column(db.DateTime, default=datetime.now(eat_tz))

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
    breed_images = db.relationship('Image', backref='breed', lazy=True, cascade="all, delete-orphan")
    breed_physical_description = db.Column(JSONB, nullable=True)
    breed_characteristics = db.Column(JSONB)
    breed_purpose = db.Column(db.String(50))
    breed_category = db.Column(db.String(50))
    feeding_nutrition = db.Column(JSONB)
    housing_environment = db.Column(JSONB)
    disease_prevention_health = db.Column(JSONB)
    breeding_reproduction = db.Column(JSONB)
    productivity_economics = db.Column(JSONB)

    farmers = db.relationship("User", secondary=farmer_breed, back_populates="breeds")

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
    
class BreedQuery(db.Model):

    query_id = db.Column(db.String(10), primary_key=True)
    chat_id = db.Column(db.String(36), db.ForeignKey('chat.chat_id'), nullable=False)
    breed_name = db.Column(db.String(100), nullable=False)
    user_query = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(eat_tz))

    def __repr__(self):
        return f"<Query {self.query_id} for {self.breed_name}>"
    
    @staticmethod
    def generate_query_id():
        last_query = BreedQuery.query.order_by(BreedQuery.query_id.desc()).first()
        if last_query:
            last_query_id = int(last_query.query_id.split("-")[1])
            new_id = f"Q-{last_query_id + 1:03d}"
        else:
            new_id = "Q-001"

        return new_id
    
class Chat(db.Model):

    chat_id = db.Column(db.String(10), primary_key=True)
    chat_title = db.Column(db.String(150))
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)  # Foreign Key
    created_at = db.Column(db.DateTime, default=datetime.now(eat_tz))

    breed_queries = db.relationship('BreedQuery', backref='chat', cascade="all, delete-orphan")

    def __repr__(self):
        return self.chat_title
    
    @staticmethod
    def generate_chat_id():
        last_chat = Chat.query.order_by(Chat.chat_id.desc()).first()
        if last_chat:
            last_chat_id = int(last_chat.chat_id.split("-")[1])
            new_id = f"C-{last_chat_id + 1:03d}"
        else:
            new_id = "C-001"

        return new_id
    
class Image(db.Model):

    image_id = db.Column(db.String(10), primary_key=True)
    image_url = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.now(eat_tz))

    breed_id = db.Column(db.String(15), db.ForeignKey('breed.breed_id'), nullable=True)
    disease_id = db.Column(db.String(15), db.ForeignKey('diseases.disease_id'), nullable=True)
    diagnosis_id = db.Column(db.String(15), db.ForeignKey('diagnosis.diagnosis_id'), nullable=True)
    
    def __repr__(self):
        if self.breed_id:
            foreign_id = self.breed_id
        elif self.disease_id:
            foreign_id = self.disease_id 
        else:
            foreign_id = self.diagnosis_id
        return f"{self.image_id} - {foreign_id}"
 
    @staticmethod
    def generate_image_id():
        last_image = Image.query.order_by(Image.image_id.desc()).first()
        if last_image:
            last_image_id = int(last_image.image_id.split("-")[1])
            new_id = f"I-{last_image_id + 1:03d}"
        else:
            new_id = "I-001"
        
        return new_id
     
class Diagnosis(db.Model):
    __tablename__ = 'diagnosis'

    diagnosis_id = db.Column(db.String(15), primary_key=True)
    symptoms_input = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    diagnosis_time = db.Column(db.DateTime, default=datetime.now(eat_tz))

    # Relationship to diseases diagnosed
    diseases_diagnosed = db.relationship('DiseasesDiagnosed', backref='diagnosis', cascade='all, delete-orphan')

    def __repr__(self):
        return self.diagnosis_id

    @staticmethod
    def generate_diagnosis_id():
        last_diagnosis = Diagnosis.query.order_by(Diagnosis.diagnosis_id.desc()).first()
        if last_diagnosis:
            last_diagnosis_id = int(last_diagnosis.diagnosis_id.split("-")[1])
            new_id = f"DIAG-{last_diagnosis_id + 1:03d}"
        else:
            new_id = "DIAG-001"
         
        return new_id


class DiseasesDiagnosed(db.Model):
    __tablename__ = 'diseases_diagnosed'

    diseases_diagnosed_id = db.Column(db.String(15), primary_key=True)
    diagnosis_id = db.Column(db.String(10), db.ForeignKey('diagnosis.diagnosis_id'), nullable=False)
    disease_id = db.Column(db.String(10), db.ForeignKey('diseases.disease_id'), nullable=False)
    probability = db.Column(db.Float, nullable=False)

    # Optional relationship for easy access to disease data
    disease = db.relationship('Disease', backref='diagnosed_cases')

    def __repr__(self):
        return self.diseases_diagnosed_id

    @staticmethod
    def generate_diseases_diagnosed_id():
        last_diseases_diagnosed = DiseasesDiagnosed.query.order_by(DiseasesDiagnosed.diseases_diagnosed_id.desc()).first()
        if last_diseases_diagnosed:
            last_diseases_diagnosed_id = int(last_diseases_diagnosed.diseases_diagnosed_id.split("-")[1])
            new_id = f"DDIAGG-{last_diseases_diagnosed_id + 1:03d}"
        else:
            new_id = "DDIAGG-001"
         
        return new_id

