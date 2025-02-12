from flask import Blueprint, jsonify, request, render_template
from app.models import User
from flask_login import login_required, current_user

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route("/home")
def home():
    return render_template("home.html")

@main_blueprint.route("/admin_dashboard", methods = ['GET'])
@login_required
def admin_dashboard():

    user_count = User.query.filter_by(user_role="farmer").count()
    if not current_user.is_admin:
        return jsonify({'message': 'Access denied! Admins only.'}), 403
    return render_template("admin/admin_dashboard.html", user_count=user_count)
