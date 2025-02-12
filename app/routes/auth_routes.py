from flask import request, render_template, redirect, url_for, flash, jsonify, Blueprint
from app.models import User
from app.extensions import db
from datetime import datetime
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash


auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone_num = request.form.get('phone_num')
        user_role = request.form.get('user_role', User.FARMER)  # Default to farmer
        location = request.form.get('location')

        if user_role not in [User.ADMIN, User.FARMER]:  
            flash('Invalid user role', 'danger')
            return redirect(url_for('auth.register'))  # Redirect back to form

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            password=hashed_password,
            email=email,
            phone_num=phone_num,
            user_role=user_role,
            location=location
        )

        db.session.add(new_user)
        db.session.commit()
        flash(f'User {username} registered successfully as {user_role}', 'success')

        return redirect(url_for('auth.login'))  # Redirect to login page after registration

    return render_template('auth/register.html')  # Render form for GET request

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # Get from form, not JSON
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):  # Correct password check
            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user)

            flash('Login successful!', 'success')

            if user.user_role == "admin":
                return redirect(url_for("main.admin_dashboard"))
            else:
                return redirect(url_for('main.home'))  # Redirect to dashboard or home page

        flash('Invalid username or password', 'danger')

    return render_template('auth/login.html')  # Render the login form for GET request

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
