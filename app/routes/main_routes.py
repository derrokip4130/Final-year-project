from flask import Blueprint, jsonify, request, render_template, redirect, url_for, abort
from app.models import User, Disease, Symptom, Breed
from app.extensions import db
from flask_login import login_required, current_user

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route("/")
def blank():
    if current_user.is_authenticated:
        if current_user.user_role == User.ADMIN:
            return redirect(url_for('main.admin_dashboard'))
    return redirect(url_for('main.home'))

@main_blueprint.route("/home")
def home():
    return render_template("home.html")

@main_blueprint.route("/select_breeds/<user_id>", methods=["GET", "POST"])
def select_breeds(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    all_breeds = Breed.query.all()  # Fetch all available breeds

    if not user:
        return redirect(url_for("main.dashboard"))  # Adjust redirect as needed

    if request.method == "POST":
        selected_breed_ids = request.form.get("selected_breeds", "").split(",")

        # Fetch selected breeds from DB
        selected_breeds = Breed.query.filter(Breed.breed_id.in_(selected_breed_ids)).all()
        
        # Assign breeds to user
        user.breeds = selected_breeds
        db.session.commit()

        return redirect(url_for("auth.login"))  # Redirect to another page after saving

    return render_template("select_breeds.html", user=user, breeds=all_breeds)


@main_blueprint.route("/admin_dashboard", methods = ['GET'])
@login_required
def admin_dashboard():
    breed_count = Breed.query.count()
    disease_count = Disease.query.count()
    user_count = User.query.filter_by(user_role="farmer").count()
    
    return render_template("admin/admin_dashboard.html", user_count=user_count, disease_count=disease_count, breed_count=breed_count)

@main_blueprint.route("/users", methods=["GET"])
@login_required
def users_page():
    users=User.query.all()
    return render_template("admin/users.html",users=users)

@main_blueprint.route("/user/<user_id>",methods=["GET","POST"])
@login_required
def user_page(user_id):
    
    user = User.query.filter_by(user_id=user_id).first()
    title = f"{user.username}"
    is_owner = current_user.user_id==user_id
    is_admin = current_user.user_role==User.ADMIN

    return render_template("admin/user_page.html",user=user, is_owner=is_owner, is_admin=is_admin,title=title)

@main_blueprint.route("/update_user/<user_id>", methods=["GET","POST"])
@login_required
def update_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    
    if request.method == "POST":
        user.username = request.form.get("username")
        user.email = request.form.get("email")
        user.phone_num = request.form.get("phone_num")
        user.location = request.form.get("location")

        try:
            db.session.commit()
            return redirect(url_for('main.user_page', user_id=user_id))
        except:
            db.session.rollback()
    
    return render_template('admin/update_user.html', user=current_user)

@main_blueprint.route("/delete_user/<user_id>",methods=["GET","POST"])
@login_required
def delete_user(user_id):
    if current_user.user_role != User.ADMIN:
        abort(403) 

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('main.users_page'))

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

@main_blueprint.route("/breeds", methods=["GET"])
@login_required
def breeds_page():
    
    breeds = Breed.query.all()
    return render_template("admin/breeds.html", breeds=breeds)

@main_blueprint.route("/add_breed", methods = ["GET","POST"])
@login_required
def add_breeds():
    if request.method == 'POST':
        breed_name = request.form.get('breed_name')
        breed_category = request.form.get('breed_category')
        breed_purpose = request.form.get('breed_purpose')

        breed_characteristics = {
            "temperament":request.form.get("temperament"),
            "farming_suitability":request.form.get("farming_suitability"),
            "climate_suitability":request.form.get("climate_suitability"),
            "special_needs":request.form.get("special_needs"),
        }

        breeding_reproduction = {
            "best_breading_age":request.form.get("best_breeding_age"),
            "egg_production":request.form.get("egg_production"),
            "brooding_requirements":request.form.get("brooding_requirements"),
            "incubation_period":request.form.get("incubation_period"),
        }


        feeding_nutrition = {
            "Chick": {
                "feed_type": request.form.get("chick_feed_type"),
                "daily_quantity": request.form.get("chick_daily_quantity"),
                "schedule": request.form.get("chick_schedule"),
            },
            "Grower": {
                "feed_type": request.form.get("grower_feed_type"),
                "daily_quantity": request.form.get("grower_daily_quantity"),
                "schedule": request.form.get("grower_schedule"),
            },
            "Broiler": {
                "feed_type": request.form.get("broiler_feed_type"),
                "daily_quantity": request.form.get("broiler_daily_quantity"),
                "schedule": request.form.get("broiler_schedule"),
            },
            "Supplementation": request.form.getlist("supplementation"),
            "Alternative_feeds": request.form.getlist("alternative_feeds"),
        }

        # Similar structure for other JSON fields
        housing_environment = {
            "Space_per_bird": request.form.get("space_per_bird"),
            "Ventilation": request.form.get("ventilation"),
            "Temperature": request.form.get("temperature"),
            "Humidity": request.form.get("humidity"),
            "Biosecurity": request.form.getlist("biosecurity"),
        }

        disease_prevention_health = {
            "common_diseases":request.form.get("common_diseases"),
            "vaccination_schedule":request.form.get("vaccination_schedule"),
        }

        productivity_economics = {
            "growth_rate":request.form.get("growth_rate"),
            "egg_laying":request.form.get("egg_laying"),
            "market_price":request.form.get("market_price"),
        }

        new_breed = Breed(
            breed_id=Breed.generate_breed_id(),
            breed_name=breed_name,
            breed_category=breed_category,
            breed_purpose=breed_purpose,
            feeding_nutrition=feeding_nutrition,
            housing_environment=housing_environment,
            breed_characteristics=breed_characteristics,
            breeding_reproduction=breeding_reproduction,
            disease_prevention_health=disease_prevention_health,
            productivity_economics=productivity_economics
        )

        db.session.add(new_breed)
        db.session.commit()
        return redirect(url_for('main.breeds_page'))

    return render_template('admin/add_breed.html')

@main_blueprint.route("/breed/<breed_id>", methods=["GET","POST"])
@login_required
def breed_page(breed_id):

    breed = Breed.query.filter_by(breed_id=breed_id).first()

    return render_template("admin/breed_page.html",breed=breed)

@main_blueprint.route("/delete_breed/<breed_id>", methods=["GET","POST"])
@login_required
def delete_breed(breed_id):

    breed = Breed.query.filter_by(breed_id=breed_id).first()
    
    if request.method =="POST":
        db.session.delete(breed)
        db.session.commit()
    return redirect(url_for('main.breeds_page'))

@main_blueprint.route("/update_breed/<breed_id>", methods=["GET","POST"])
@login_required
def update_breed(breed_id):

    breed = Breed.query.filter_by(breed_id=breed_id).first()
    
    if request.method =="POST":
            breed.breed_name = request.form.get('breed_name')
            breed.breed_category = request.form.get('breed_category')
            breed.breed_purpose = request.form.get('breed_purpose')

            breed.breed_characteristics = {
                "temperament":request.form.get("temperament"),
                "farming_suitability":request.form.get("farming_suitability"),
                "climate_suitability":request.form.get("climate_suitability"),
                "special_needs":request.form.get("special_needs"),
            }

            breed.breeding_reproduction = {
                "best_breading_age":request.form.get("best_breeding_age"),
                "egg_production":request.form.get("egg_production"),
                "brooding_requirements":request.form.get("brooding_requirements"),
                "incubation_period":request.form.get("incubation_period"),
            }

            breed.feeding_nutrition = {
                "Chick": {
                    "feed_type": request.form.get("chick_feed_type"),
                    "daily_quantity": request.form.get("chick_daily_quantity"),
                    "schedule": request.form.get("chick_schedule"),
                },
                "Grower": {
                    "feed_type": request.form.get("grower_feed_type"),
                    "daily_quantity": request.form.get("grower_daily_quantity"),
                    "schedule": request.form.get("grower_schedule"),
                },
                "Broiler": {
                    "feed_type": request.form.get("broiler_feed_type"),
                    "daily_quantity": request.form.get("broiler_daily_quantity"),
                    "schedule": request.form.get("broiler_schedule"),
                },
                "Supplementation": request.form.getlist("supplementation"),
                "Alternative_feeds": request.form.getlist("alternative_feeds"),
            }

            breed.housing_environment = {
                "Space_per_bird": request.form.get("space_per_bird"),
                "Ventilation": request.form.get("ventilation"),
                "Temperature": request.form.get("temperature"),
                "Humidity": request.form.get("humidity"),
                "Biosecurity": request.form.getlist("biosecurity"),
            }

            breed.disease_prevention_health = {
                "common_diseases":request.form.get("common_diseases"),
                "vaccination_schedule":request.form.get("vaccination_schedule"),
            }

            breed.productivity_economics = {
                "growth_rate":request.form.get("growth_rate"),
                "egg_laying":request.form.get("egg_laying"),
                "market_price":request.form.get("market_price"),
            }
            try:
                db.session.commit()
                print(breed)
                return redirect(url_for('main.breed_page', breed_id=breed.breed_id))
            except:
                db.session.rollback()

    return render_template("admin/update_breeds.html",breed=breed)


@main_blueprint.route("/breed_queries")
@login_required
def breed_queries():
    user = User.query.get(current_user.user_id)  # Get the logged-in user
    selected_breeds = user.breeds  # Fetch breeds the user has selected
    return render_template("breed_queries.html", breeds=selected_breeds)
