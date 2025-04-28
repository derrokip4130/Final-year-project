import json, pytz
from app import create_app, db
from app.models import Breed, Disease, Symptom
from sqlalchemy import inspect
from datetime import datetime

app = create_app()
eat_tz = pytz.timezone("Africa/Nairobi")

with app.app_context():
    inspector = inspect(db.engine)

    # Get all existing table names
    existing_tables = inspector.get_table_names()
    
    # Get all table names defined in models.py
    declared_tables = db.metadata.tables.keys()

    # Check if any declared table already exists
    if any(table in existing_tables for table in declared_tables):
        print("Tables already exist.")
    else:
        db.create_all()
        print("Tables created.")

        # Load breeds from JSON
        with open('app/datasets/poultry_breeds.json') as file:
            breeds_data = json.load(file)

        for name, data in breeds_data.items():
            if Breed.query.filter_by(breed_name=name).first():
                continue  # Skip if already added

            breed = Breed(
                breed_id=Breed.generate_breed_id(),
                breed_name=name,
                breed_physical_description=data.get("physical_description"),
                breed_characteristics=data.get("breed_characteristics"),
                breed_purpose=data.get("breed_purpose", "Not specified"),
                breed_category=data.get("breed_category", "Unknown"),
                feeding_nutrition=data.get("feeding_and_nutrition"),
                housing_environment=data.get("housing_and_environment"),
                disease_prevention_health=data.get("disease_prevention_and_health"),
                breeding_reproduction=data.get("breeding_and_reproduction"),
                productivity_economics=data.get("productivity_and_economics")
            )
            db.session.add(breed)

        with open('app/datasets/poultry_diseases.json') as f:
            data = json.load(f)
            
        for disease_entry in data["poultry_diseases"]:
            # Generate unique disease ID
            disease_id = Disease.generate_disease_id()

            # Combine lists into readable strings
            causes = "; ".join(disease_entry.get("causes", []))
            prevention = "\n".join(disease_entry.get("preventive_measures", []))
            treatment_options = "; ".join(disease_entry.get("treatments", []))
            # Create Disease object
            disease = Disease(
                disease_id=disease_id,
                disease_name=disease_entry["disease_name"],
                disease_description=disease_entry["description"],
                disease_prevention_tips=prevention,
                causes=causes,
                disease_treatment_options=treatment_options,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )

            # Add disease to session
            db.session.add(disease)

            # Handle symptoms
            for name in disease_entry["symptoms"]:
                # Check if symptom already exists
                symptom = Symptom.query.filter_by(symptom_name=name).first()
                if not symptom:
                    symptom = Symptom(
                        symptom_id=Symptom.generate_symptom_id(),
                        symptom_name=name,
                        symptom_description=None
                    )
                    db.session.add(symptom)

                    # Link symptom to disease
                    disease.symptoms.append(symptom)

        db.session.commit()
        print("Breeds and Disease data loaded.")
