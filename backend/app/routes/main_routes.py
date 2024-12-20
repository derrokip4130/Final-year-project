from flask import Blueprint, jsonify, request
from app.models import User, db

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route("/home")
def home():
    return jsonify({"message": "Welcome to the Poultry Care API!"})
