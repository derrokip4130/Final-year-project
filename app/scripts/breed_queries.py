import json, re, cohere, os, requests
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

valid_categories = {
    "Feeding and Nutrition": ["Chick", "Grower", "Broiler", "Supplementation", "Alternative_feeds"],
    "Housing and Environment": ["Space_per_bird", "Ventilation", "Temperature", "Humidity", "Biosecurity"],
    "Disease Prevention and Health": ["Common_diseases", "Vaccination_schedule", "Signs_of_illness", "Deworming"],
    "Breed Characteristics": ["Temperament", "Farming_suitability", "Climate_adaptability", "Special_needs"],
    "Purpose": [],
    "Category": []
}

def get_response(selected_breed, user_input):
    # Fetch breed data dynamically
    response = requests.get(f"http://127.0.0.1:5000/get_breed_data/{selected_breed}")
    
    if response.status_code != 200:
        return "Error: Breed data not found."

    dataset = response.json()
    
    # Extract breed-specific data
    breed_data = dataset.get(selected_breed, {})

    # Modify prompt to allow multiple categories
    response = co.chat(
        model="command-r-plus",
        message=f"""
        Identify the user's intent based on the following valid categories.
        A user query may be related to multiple categories.

        {json.dumps(valid_categories, indent=4)}

        User input: {user_input}

        Return ONLY a valid JSON output without extra words. Example:

        {{
            "intents": [
                {{"intent": "Feeding and Nutrition", "subcategory": "Chick"}},
                {{"intent": "Purpose"}}
            ]
        }}
        """
    )

    # Extract JSON from response
    match = re.search(r"\{.*\}", response.text, re.DOTALL)

    if match:
        json_text = match.group(0)
        try:
            intent_data = json.loads(json_text)
            detected_intents = intent_data.get("intents", [])

        except json.JSONDecodeError:
            detected_intents = []
    else:
        detected_intents = []

    # Retrieve relevant information for each detected category
    results = []
    for item in detected_intents:
        intent = item.get("intent", "Unknown")
        subcategory = item.get("subcategory", None)  

        # Validate intent
        if intent not in valid_categories:
            continue  # Skip invalid categories
        
        # Fetch data for intent/subcategory
        if not valid_categories[intent]:  # If no subcategories exist
            result = breed_data.get(intent, "No data available.")
        else:
            if subcategory not in valid_categories[intent]:  
                subcategory = None  # Reset invalid subcategory

            result = breed_data.get(intent, {}).get(subcategory, breed_data.get(intent, "No data available."))

        # Handle list-based data representation
        if isinstance(result, list):
            formatted_result = "\n".join(f"- {item}" for item in result)
        else:
            formatted_result = result

        results.append(f"**{intent}**: {formatted_result}")

    if not results:
        return "Sorry, I couldn't find relevant information."

    # Generate final response
    final_response = co.chat(
        model="command-r-plus",
        message=f"""
        Based on the extracted data for the {selected_breed} breed, generate a clear response covering multiple aspects.

        Breed: {selected_breed}
        Data:
        {json.dumps(results, indent=4)}

        User asked: {user_input}

        Ensure the response is structured, concise, and naturally includes the breed name.
        Format lists using bullet points if necessary.
        """,
        temperature=0.8,
        k=50
    )

    return final_response.text

if __name__ == "__main__":
    print(get_response("Hubbard Flex", "What are the signs of illness and feeding requirements?"))
