import torch, requests
import torchvision.transforms as transforms
from PIL import Image
import torchvision.models as models
import torch.nn as nn
from io import BytesIO
from collections import defaultdict

def analyze_image(image_url, class_names=["Infectious Coryza", "Fowl Pox", "Newcastle Disease"]):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet50(weights=None)  # Initialize ResNet without pretrained weights

    # Modify final layer to match trained model
    num_classes = 3  # Ensure this matches what you trained on
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(model.fc.in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )

    # Load trained weights
    model.load_state_dict(torch.load("app/scripts/poultry_diseases_final_1.pth", map_location=device))
    model.to(device)
    model.eval()  # Set to evaluation mode

    # Define image transformations (should match training preprocessing)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

    # **Download Image from URL**
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download image. Status Code: {response.status_code}")
    
    image = Image.open(BytesIO(response.content)).convert("RGB")

    # Apply transformations
    image = transform(image).unsqueeze(0).to(device)  # Add batch dimension

    # Perform inference
    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)  # Convert logits to probabilities
        probabilities = probabilities.squeeze().tolist()  # Convert to list
    
    # Get predicted class
    predicted_idx = torch.argmax(torch.tensor(probabilities)).item()
    predicted_disease = class_names[predicted_idx]

    # Format results with percentages
    results = {class_names[i]: round(prob * 100, 2) for i, prob in enumerate(probabilities)}

    return predicted_disease, results

def diagnose_symptoms(symptoms_input):
    disease_dataset = []
    seen_diseases = {}  # Dictionary to track unique diseases by ID

    # Step 1: Fetch diseases for each symptom
    for symptom in symptoms_input:
        response = requests.get(f'http://127.0.0.1:5000/search_disease/{symptom}')
        if response.status_code == 200:
            diseases = response.json().get("diseases", [])

            for disease in diseases:
                disease_id = disease["disease_id"]

                if disease_id not in seen_diseases:
                    seen_diseases[disease_id] = disease

    diseases = list(seen_diseases.values())

    if not diseases:
        return None, {}  # No diseases found

    # Step 2: Compute symptom occurrence across diseases
    symptom_count = defaultdict(int)
    for disease in diseases:
        for symptom in set(disease["symptoms"]):
            symptom_count[symptom] += 1

    # Step 3: Compute disease priors
    disease_priors = {}
    for disease in diseases:
        disease_symptoms = set(disease["symptoms"])
        disease_priors[disease["disease_name"]] = sum(1 / symptom_count[s] for s in disease_symptoms)

    # Normalize priors
    total_prior = sum(disease_priors.values())
    for disease in disease_priors:
        disease_priors[disease] /= total_prior

    # Step 4: Compute hybrid probabilities
    user_symptoms = set(symptoms_input)
    probabilities = {}
    total_prob = 0

    for disease in diseases:
        disease_symptoms = set(disease["symptoms"])
        match_count = len(user_symptoms & disease_symptoms)
        total_symptoms = len(disease_symptoms)

        # Bayesian likelihood P(S | D)
        likelihood = match_count / total_symptoms if total_symptoms else 0

        # Hybrid probability
        hybrid_score = likelihood * disease_priors[disease["disease_name"]]
        probabilities[disease["disease_name"]] = hybrid_score
        total_prob += hybrid_score

    # Normalize probabilities
    if total_prob > 0:
        for disease in probabilities:
            probabilities[disease] = round(probabilities[disease] / total_prob * 100, 2)
    else:
        probabilities = {d: 0 for d in probabilities}  # Avoid division by zero

    # Get the disease with the highest probability
    predicted_disease = max(probabilities, key=probabilities.get, default=None)

    return predicted_disease, probabilities

def process_diagnosis(symptoms_input=None, image_url=None):
    symptom_results = {}
    image_results = {}

    # Case 1: Symptoms only
    if symptoms_input and not image_url:
        predicted_disease, symptom_results = diagnose_symptoms(symptoms_input)
        return {"method": "symptoms_only", "predicted_disease": predicted_disease, "results": symptom_results}

    # Case 2: Image only
    if image_url and not symptoms_input:
        predicted_disease, image_results = analyze_image(image_url)
        return {"method": "image_only", "predicted_disease": predicted_disease, "results": image_results}

    # Case 3: Both symptoms and image
    if symptoms_input and image_url:
        pred_symptoms, symptom_results = diagnose_symptoms(symptoms_input)
        pred_image, image_results = analyze_image(image_url)

        # Normalize both probability distributions
        total_symptom_prob = sum(symptom_results.values())
        total_image_prob = sum(image_results.values())

        for disease in symptom_results:
            symptom_results[disease] = symptom_results[disease] / total_symptom_prob if total_symptom_prob else 0

        for disease in image_results:
            image_results[disease] = image_results[disease] / total_image_prob if total_image_prob else 0

        # Weighted Combination (adjust weight as needed)
        weight_symptoms = 0.6  # Give more weight to symptoms
        weight_image = 0.4

        combined_results = {}
        for disease in set(symptom_results.keys()).union(set(image_results.keys())):
            combined_results[disease] = (
                weight_symptoms * symptom_results.get(disease, 0) +
                weight_image * image_results.get(disease, 0)
            )

        # Normalize and convert to percentages
        total_combined = sum(combined_results.values())
        for disease in combined_results:
            combined_results[disease] = round(combined_results[disease] / total_combined * 100, 2) if total_combined else 0

        # Get the final predicted disease
        predicted_disease = max(combined_results, key=combined_results.get, default=None)

        return {"method": "both", "predicted_disease": predicted_disease, "results": combined_results}

    return {"error": "No input provided"}


if __name__ == "__main__":
    image_url = "https://d1lg8auwtggj9x.cloudfront.net/images/newcastledisease.width-820.jpg"
    symptoms = ["coughing","sneezing","twisted neck", "swelling of the face"]
    print(process_diagnosis(image_url=image_url))
