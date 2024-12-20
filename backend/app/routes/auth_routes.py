from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db, bcrypt, jwt, blacklist
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Find the user by username
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate a new token and save it to the user
    token = User.generate_token()
    user.token = token
    db.session.commit()

    return jsonify({"message": "Login successful", "token": token}), 200

@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization')

    if not token or not token.startswith('Bearer '):
        return jsonify({"error": "Invalid or missing token"}), 401

    token = token.split(" ")[1]  # Extract token from Bearer <token>

    # Find user by token
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({"error": "Invalid token"}), 401

    # Invalidate the token
    user.token = None
    db.session.commit()

    return jsonify({"message": "Logged out successfully"}), 200

@auth_blueprint.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')

    if not token or not token.startswith('Bearer '):
        return jsonify({"error": "Token is required"}), 401

    token = token.split(" ")[1]  # Extract token from Bearer <token>

    # Find user by token
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({"error": "Invalid token"}), 401

    return jsonify({"message": f"Welcome {user.username}!"}), 200
