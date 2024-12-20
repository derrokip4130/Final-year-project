from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()

# Simple blacklist (could be replaced with Redis or a database)
blacklist = set()

# JWT token identity loader (for checking blacklisted tokens)
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['identity'] in blacklist
