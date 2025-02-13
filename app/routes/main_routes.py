from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from app.models import User, Disease, Symptom
from app.extensions import db
from flask_login import login_required, current_user

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route("/home")
def home():
    return render_template("home.html")

@main_blueprint.route("/admin_dashboard", methods = ['GET'])
@login_required
def admin_dashboard():
    disease_count = Disease.query.count()
    user_count = User.query.filter_by(user_role="farmer").count()
    if not current_user.is_admin:
        return jsonify({'message': 'Access denied! Admins only.'}), 403
    return render_template("admin/admin_dashboard.html", user_count=user_count, disease_count=disease_count)

@main_blueprint.route("/diseases", methods = ["GET"])
@login_required
def diseases_page():
    diseases = Disease.query.all()
    return render_template("admin/diseases.html", diseases=diseases)

@main_blueprint.route('/add_disease', methods=['GET', 'POST'])
@login_required
def add_disease():
    if request.method == 'POST':
        disease_name = request.form.get('disease_name')
        disease_description = request.form.get('disease_description')
        causes = request.form.get('causes')
        symptom_ids = request.form.getlist('symptoms')

        new_disease = Disease(
            disease_id=Disease.generate_disease_id(),  # Auto-generate ID
            disease_name=disease_name,
            disease_description=disease_description,
            causes=causes
        )
        
        # Add symptoms if selected
        if symptom_ids:
            symptoms = Symptom.query.filter(Symptom.symptom_id.in_(symptom_ids)).all()
            new_disease.symptoms.extend(symptoms)

        db.session.add(new_disease)
        db.session.commit()

        flash('Disease added successfully!', 'success')
        return redirect(url_for('main.diseases_page'))

    symptoms = Symptom.query.all()
    return render_template('admin/add_disease.html', symptoms=symptoms)

@main_blueprint.route('/add_symptom_ajax', methods=['POST'])
@login_required
def add_symptom_ajax():
    data = request.get_json()
    symptom_name = data.get("symptom_name")
    symptom_description = data.get("symptom_description") or None  # Allow empty description

    if not symptom_name:
        return jsonify({"success": False, "message": "Symptom name is required"}), 400

    new_symptom = Symptom(
        symptom_id=Symptom.generate_symptom_id(),
        symptom_name=symptom_name,
        symptom_description=symptom_description
    )
    db.session.add(new_symptom)
    db.session.commit()

    return jsonify({"success": True, "symptom_id": new_symptom.symptom_id})

