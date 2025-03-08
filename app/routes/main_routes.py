import requests,  pytz
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, abort
from app.models import User, Disease, Symptom, Breed, BreedQuery, Chat
from app.extensions import db
from flask_login import login_required, current_user
from app.scripts.breed_queries import get_response
from datetime import datetime


main_blueprint = Blueprint('main', __name__)

eat_tz = pytz.timezone("Africa/Nairobi")

@main_blueprint.route("/")
def blank():
    if current_user.is_authenticated:
        if current_user.user_role == User.ADMIN:
            return redirect(url_for('main.admin_dashboard'))
    return redirect(url_for('main.home'))

@main_blueprint.route("/home")
def home():
    return render_template("home.html")

@main_blueprint.route("/admin_dashboard", methods = ['GET'])
@login_required
def admin_dashboard():
    breed_count = Breed.query.count()
    disease_count = Disease.query.count()
    user_count = User.query.filter_by(user_role="farmer").count()
    if not current_user.is_admin:
        abort(403)
    return render_template("admin/admin_dashboard.html", user_count=user_count, disease_count=disease_count, breed_count=breed_count)

@main_blueprint.route("/users", methods=["GET"])
@login_required
def users_page():
    if not current_user.is_admin:
        abort(403)
    users=User.query.all()
    return render_template("admin/users.html",users=users)

@main_blueprint.route("/user/<user_id>",methods=["GET","POST"])
@login_required
def user_page(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.filter_by(user_id=user_id).first()
    title = f"{user.username}"
    is_owner = current_user.user_id==user_id
    is_admin = current_user.user_role==User.ADMIN

    return render_template("admin/user_page.html",user=user, is_owner=is_owner, is_admin=is_admin,title=title)

@main_blueprint.route("/update_user/<user_id>", methods=["GET","POST"])
@login_required
def update_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not current_user.is_admin:
        abort(403)
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
    if not current_user.is_admin:
        abort(403)
    diseases = Disease.query.all()
    return render_template("admin/diseases.html", diseases=diseases)

@main_blueprint.route('/add_disease', methods=['GET', 'POST'])
@login_required
def add_disease():
    if not current_user.is_admin:
        abort(403)
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
    if not current_user.is_admin:
        abort(403)
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

@main_blueprint.route("/disease/<disease_id>",methods=["GET","POST"])
@login_required
def disease_page(disease_id):

    disease = Disease.query.filter_by(disease_id=disease_id).first()

    return render_template("admin/disease_page.html",disease=disease)

@main_blueprint.route("/update_disease/<disease_id>",methods=["GET","POST"])
@login_required
def update_disease(disease_id):

    disease = Disease.query.filter_by(disease_id=disease_id).first()
    symptoms = Symptom.query.all()

    if request.method == "POST":
        disease.disease_name = request.form.get('disease_name')
        disease.disease_description = request.form.get('disease_description')
        disease.causes = request.form.get('causes')
        updated_symptom_ids = request.form.getlist('symptoms')  # List of selected symptoms
        
        # Clear existing symptoms to avoid duplicates
        disease.symptoms.clear()

        # Fetch and add newly selected symptoms
        if updated_symptom_ids:
            selected_symptoms = Symptom.query.filter(Symptom.symptom_id.in_(updated_symptom_ids)).all()
            disease.symptoms.extend(selected_symptoms)

        try:
            db.session.commit()
            return redirect(url_for('main.disease_page', disease_id=disease.disease_id))
        except:
            db.session.rollback()

    return render_template("admin/update_disease.html",disease=disease,symptoms=symptoms)

@main_blueprint.route("/delete_disease/<disease_id>", methods=["GET","POST"])
@login_required
def delete_disease(disease_id):
    if not current_user.is_admin:
        abort(403)
    disease = Disease.query.filter_by(disease_id=disease_id).first()
    
    if request.method =="POST":
        db.session.delete(disease)
        db.session.commit()
    return redirect(url_for('main.diseases_page'))

@main_blueprint.route("/breeds", methods=["GET"])
@login_required
def breeds_page():
    if not current_user.is_admin:
        abort(403)
    breeds = Breed.query.all()
    return render_template("admin/breeds.html", breeds=breeds)

@main_blueprint.route("/add_breed", methods=["GET", "POST"])
@login_required
def add_breeds():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        breed_name = request.form.get('breed_name')

        feeding_nutrition = {
            "Chick": {
                "feed_type": request.form.get("Feeding_and_Nutrition[Chick][feed_type]"),
                "daily_quantity": request.form.get("Feeding_and_Nutrition[Chick][daily_quantity]"),
                "schedule": request.form.get("Feeding_and_Nutrition[Chick][schedule]"),
            },
            "Grower": {
                "feed_type": request.form.get("Feeding_and_Nutrition[Grower][feed_type]"),
                "daily_quantity": request.form.get("Feeding_and_Nutrition[Grower][daily_quantity]"),
                "schedule": request.form.get("Feeding_and_Nutrition[Grower][schedule]"),
            },
            "Broiler": {
                "feed_type": request.form.get("Feeding_and_Nutrition[Broiler][feed_type]"),
                "daily_quantity": request.form.get("Feeding_and_Nutrition[Broiler][daily_quantity]"),
                "schedule": request.form.get("Feeding_and_Nutrition[Broiler][schedule]"),
            },
            "Supplementation": request.form.get("Feeding_and_Nutrition[Supplementation]", "").split(","),
            "Alternative_feeds": request.form.get("Feeding_and_Nutrition[Alternative_feeds]", "").split(","),
        }

        housing_environment = {
            "Space_per_bird": request.form.get("Housing_and_Environment[Space_per_bird]"),
            "Ventilation": request.form.get("Housing_and_Environment[Ventilation]"),
            "Temperature": request.form.get("Housing_and_Environment[Temperature]"),
            "Humidity": request.form.get("Housing_and_Environment[Humidity]"),
            "Biosecurity": request.form.get("Housing_and_Environment[Biosecurity]", "").split(","),
        }

        disease_prevention_health = {
            "common_diseases": request.form.get("Disease_Prevention_and_Health[Common_diseases]", "").split(","),
            "vaccination_schedule": [],
            "deworming": request.form.get("Disease_Prevention_and_Health[Deworming]")
        }

        # Process dynamic vaccination schedule
        index = 0
        while request.form.get(f"Disease_Prevention_and_Health[Vaccination_schedule][{index}][Disease]"):
            disease_prevention_health["vaccination_schedule"].append({
                "Disease": request.form.get(f"Disease_Prevention_and_Health[Vaccination_schedule][{index}][Disease]"),
                "Age": request.form.get(f"Disease_Prevention_and_Health[Vaccination_schedule][{index}][Age]"),
                "Method": request.form.get(f"Disease_Prevention_and_Health[Vaccination_schedule][{index}][Method]"),
            })
            index += 1

        disease_prevention_health["Signs_of_illness"] = request.form.get(
            "Disease_Prevention_and_Health[Signs_of_illness]", "").split(",")

        disease_prevention_health["Deworming"] = request.form.get("Disease_Prevention_and_Health[Deworming]")

        breeding_reproduction = {
            "best_breeding_age": request.form.get("Breeding_and_Reproduction[Best_breeding_age]"),
            "egg_production": request.form.get("Breeding_and_Reproduction[Egg_production]"),
            "brooding_requirements": request.form.get("Breeding_and_Reproduction[Brooding_requirements]"),
            "incubation_methods": request.form.get("Breeding_and_Reproduction[Incubation_methods]"),
        }

        productivity_economics = {
            "growth_rate": request.form.get("Productivity_and_Economics[Growth_rate]"),
            "egg_laying": request.form.get("Productivity_and_Economics[Egg_laying]"),
            "market_price": request.form.get("Productivity_and_Economics[Market_price]"),
            "profit_maximization": request.form.get("Productivity_and_Economics[Profit_maximization]", "").split(","),
        }

        breed_characteristics = {
            "temperament": request.form.get("Breed_Characteristics[Temperament]"),
            "farming_suitability": request.form.get("Breed_Characteristics[Farming_suitability]"),
            "climate_adaptability": request.form.get("Breed_Characteristics[Climate_adaptability]"),
            "special_needs": request.form.get("Breed_Characteristics[Special_needs]"),
        }

        # Create breed object
        new_breed = Breed(
            breed_id=Breed.generate_breed_id(),
            breed_name=breed_name,
            feeding_nutrition=feeding_nutrition,
            housing_environment=housing_environment,
            disease_prevention_health=disease_prevention_health,
            breeding_reproduction=breeding_reproduction,
            productivity_economics=productivity_economics,
            breed_characteristics=breed_characteristics
        )

        # Add and commit to the database
        db.session.add(new_breed)
        db.session.commit()
        return redirect(url_for('main.breeds_page'))

    return render_template('admin/add_breed.html')


@main_blueprint.route("/breed/<breed_id>", methods=["GET","POST"])
@login_required
def breed_page(breed_id):
    if not current_user.is_admin:
        abort(403)
    breed = Breed.query.filter_by(breed_id=breed_id).first()
    print(breed.productivity_economics)

    return render_template("admin/breed_page.html",breed=breed)

@main_blueprint.route("/delete_breed/<breed_id>", methods=["GET","POST"])
@login_required
def delete_breed(breed_id):
    if not current_user.is_admin:
        abort(403)
    breed = Breed.query.filter_by(breed_id=breed_id).first()
    
    if request.method =="POST":
        db.session.delete(breed)
        db.session.commit()
    return redirect(url_for('main.breeds_page'))

@main_blueprint.route("/update_breed/<string:breed_id>", methods=["GET", "POST"])
@login_required
def update_breed(breed_id):
    if not current_user.is_admin:
        abort(403)

    breed = Breed.query.filter_by(breed_id=breed_id).first()
    if not breed:
        abort(404)

    if request.method == "POST":
        breed.breed_name = request.form.get("breed_name")

        # Feeding and Nutrition
        breed.feeding_nutrition = {
            "Chick": {
                "feed_type": request.form.get("Feeding_and_Nutrition[Chick][feed_type]"),
                "daily_quantity": request.form.get("Feeding_and_Nutrition[Chick][daily_quantity]"),
                "schedule": request.form.get("Feeding_and_Nutrition[Chick][schedule]"),
            },
            "Grower": {
                "feed_type": request.form.get("Feeding_and_Nutrition[Grower][feed_type]"),
                "daily_quantity": request.form.get("Feeding_and_Nutrition[Grower][daily_quantity]"),
                "schedule": request.form.get("Feeding_and_Nutrition[Grower][schedule]"),
            },
            "Broiler": {
                "feed_type": request.form.get("Feeding_and_Nutrition[Broiler][feed_type]"),
                "daily_quantity": request.form.get("Feeding_and_Nutrition[Broiler][daily_quantity]"),
                "schedule": request.form.get("Feeding_and_Nutrition[Broiler][schedule]"),
            },
            "Supplementation": request.form.get("Feeding_and_Nutrition[Supplementation]", "").split(","),
            "Alternative_feeds": request.form.get("Feeding_and_Nutrition[Alternative_feeds]", "").split(","),
        }

        # Housing and Environment
        breed.housing_environment = {
            "Space_per_bird": request.form.get("Housing_and_Environment[Space_per_bird]"),
            "Ventilation": request.form.get("Housing_and_Environment[Ventilation]"),
            "Temperature": request.form.get("Housing_and_Environment[Temperature]"),
            "Humidity": request.form.get("Housing_and_Environment[Humidity]"),
            "Biosecurity": request.form.get("Housing_and_Environment[Biosecurity]", "").split(","),
        }

        # Disease Prevention and Health
        disease_prevention_health = {
            "common_diseases": request.form.get("Disease_Prevention_and_Health[Common_diseases]", "").split(","),
            "vaccination_schedule": [],
            "deworming": request.form.get("Disease_Prevention_and_Health[Deworming]"),
        }

        # Process dynamic vaccination schedule
        index = 0
        while request.form.get(f"Disease_Prevention_and_Health[Vaccination_schedule][{index}][Disease]"):
            disease_prevention_health["vaccination_schedule"].append({
                "Disease": request.form.get(f"Disease_Prevention_and_Health[Vaccination_schedule][{index}][Disease]"),
                "Age": request.form.get(f"Disease_Prevention_and_Health[Vaccination_schedule][{index}][Age]"),
                "Method": request.form.get(f"Disease_Prevention_and_Health[Vaccination_schedule][{index}][Method]"),
            })
            index += 1

        disease_prevention_health["Signs_of_illness"] = request.form.get(
            "Disease_Prevention_and_Health[Signs_of_illness]", "").split(",")

        breed.disease_prevention_health = disease_prevention_health

        # Breeding and Reproduction
        breed.breeding_reproduction = {
            "best_breeding_age": request.form.get("Breeding_and_Reproduction[Best_breeding_age]"),
            "egg_production": request.form.get("Breeding_and_Reproduction[Egg_production]"),
            "brooding_requirements": request.form.get("Breeding_and_Reproduction[Brooding_requirements]"),
            "incubation_methods": request.form.get("Breeding_and_Reproduction[Incubation_methods]"),
        }

        # Productivity and Economics
        breed.productivity_economics = {
            "growth_rate": request.form.get("Productivity_and_Economics[Growth_rate]"),
            "egg_laying": request.form.get("Productivity_and_Economics[Egg_laying]"),
            "market_price": request.form.get("Productivity_and_Economics[Market_price]"),
            "profit_maximization": request.form.get("Productivity_and_Economics[Profit_maximization]", "").split(","),
        }

        # Breed Characteristics
        breed.breed_characteristics = {
            "temperament": request.form.get("Breed_Characteristics[Temperament]"),
            "farming_suitability": request.form.get("Breed_Characteristics[Farming_suitability]"),
            "climate_adaptability": request.form.get("Breed_Characteristics[Climate_adaptability]"),
            "special_needs": request.form.get("Breed_Characteristics[Special_needs]"),
        }

        # Commit changes to the database
        try:
            db.session.commit()
            return redirect(url_for('main.breed_page', breed_id=breed.breed_id))
        except:
            db.session.rollback()

    return render_template("admin/update_breeds.html", breed=breed)



@main_blueprint.route("/breed_queries", methods=["GET","POST"])
@login_required
def breed_queries():
    breeds = Breed.query.all()
    chats = Chat.query.all()

    return render_template("breed_queries.html", breeds=breeds, chats=chats)

@main_blueprint.route("/disease_diagnosis", methods=["GET","POST"])
@login_required
def disease_diagnosis():

    return render_template("disease_diagnosis.html")

@main_blueprint.route("/get_breed_data/<breed_name>", methods=["GET"])
#@login_required
def get_breed_data(breed_name):
    try:
        breed = Breed.query.filter_by(breed_name=breed_name).first()

        if not breed:
            return jsonify({"error": "Breed not found"}), 404

        dataset = {
            "breed_name": breed.breed_name,
            "Purpose": breed.breed_purpose,
            "Category": breed.breed_category,
            "Feeding and Nutrition": {
                stage: {
                    "feed_type": breed.feeding_nutrition.get(stage, {}).get("feed_type", "N/A"),
                    "daily_quantity": breed.feeding_nutrition.get(stage, {}).get("daily_quantity", "N/A"),
                    "schedule": breed.feeding_nutrition.get(stage, {}).get("schedule", "N/A"),
                } for stage in ["Chick", "Grower"]
            },
            "Housing and Environment": {
                key: breed.housing_environment.get(key, "N/A") for key in [
                    "Space_per_bird", "Ventilation", "Temperature", "Humidity", "Biosecurity"
                ]
            },
            "Disease Prevention and Health": {
                key: breed.disease_prevention_health.get(key, "N/A") for key in [
                    "common_diseases", "vaccination_schedule", "deworming"
                ]
            },
            "Breeding and Reproduction": {
                key: breed.breeding_reproduction.get(key, "N/A") for key in [
                    "best_breeding_age", "egg_production", "brooding_requirements", "incubation_period"
                ]
            },
            "Productivity and Economics": {
                key: breed.productivity_economics.get(key, "N/A") for key in [
                    "growth_rate", "egg_laying", "market_price"
                ]
            },
            "Breed Characteristics": {
                key: breed.breed_characteristics.get(key, "N/A") for key in [
                    "temperament", "farming_suitability", "climate_suitability", "special_needs"
                ]
            }
        }

        return dataset

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@main_blueprint.route("/get_chat_response", methods=["POST"])
@login_required
def get_chat_response():
    data = request.get_json()
    breed = data.get("breed")
    message = data.get("message")
    chat_id = data.get("chat_id")

    user_id = str(current_user.user_id)

    if not breed or not message:
        return jsonify({"error": "Invalid input"}), 400

    chat = None
    is_new_chat = False  # Track if a new chat is created

    if chat_id:
        chat = Chat.query.filter_by(chat_id=chat_id, user_id=user_id).first()

    if not chat:
        is_new_chat = True  # New chat is being created
        chat_title = f"{breed} - {message[:30]}..." if len(message) > 30 else f"{breed} - {message}"
        chat = Chat(
            chat_id=Chat.generate_chat_id(),
            chat_title=chat_title,
            user_id=user_id,
            created_at=datetime.now(eat_tz)
        )
        db.session.add(chat)
        db.session.commit()

    response_text = get_response(breed, message)

    new_query = BreedQuery(
        query_id=BreedQuery.generate_query_id(),
        chat_id=chat.chat_id,
        breed_name=breed,
        user_query=message,
        bot_response=response_text,
        timestamp=datetime.now(eat_tz)
    )

    db.session.add(new_query)
    db.session.commit()
    
    return jsonify({
        "response": response_text,
        "chat_id": chat.chat_id,
        "chat_title": chat.chat_title if is_new_chat else None  # Send chat title if it's a new chat
    })

@main_blueprint.route("/get_chat_queries/<chat_id>", methods=["GET"])
@login_required
def get_chat_queries(chat_id):
    chat = Chat.query.filter_by(chat_id=chat_id, user_id=current_user.user_id).first()
    
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    queries = BreedQuery.query.filter_by(chat_id=chat_id).order_by(BreedQuery.timestamp).all()

    query_list = [
        {"user_query": query.user_query, "bot_response": query.bot_response}
        for query in queries
    ]

    return jsonify({"queries": query_list})
