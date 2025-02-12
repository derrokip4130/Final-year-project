from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'defaultsecretkey')  # Fallback to 'defaultsecretkey' if not set
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///default.db')  # Fallback to SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False

