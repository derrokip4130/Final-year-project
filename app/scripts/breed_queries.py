import json, re, cohere, os, requests
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

valid_categories = {
    "Feeding and Nutrition": ["Chick", "Grower", "Broiler", "Supplementation", "Alternative_feeds"],
    "Housing and Environment": ["Space_per_bird", "Ventilation", "Temperature", "Humidity", "Biosecurity"],
    "Disease Prevention and Health": ["Common_diseases", "Vaccination_schedule", "Signs_of_illness", "Deworming"],
    "Breed Characteristics": ["Temperament", "Farming_suitability", "Climate_adaptability", "Special_needs"],
    "General Poultry Care": ["Injection_types", "Biosecurity_measures", "Common_treatments"],
    "Purpose": [],
    "Category": []
}

def format_vaccination_schedule(vaccination_data):
    """Format vaccination details as a structured list."""
    if not isinstance(vaccination_data, list):
        return "No vaccination data available."

    formatted_schedule = "\n".join(
        f"- **Age:** {entry['Age']}, **Disease:** {entry['Disease']}, **Method:** {entry['Method']}"
        for entry in vaccination_data
    )
    return formatted_schedule

def get_response(selected_breed, user_input):
    # Fetch breed data dynamically
    response = requests.get(f"http://127.0.0.1:5000/get_breed_data/{selected_breed}")
    
    if response.status_code != 200:
        return "Error: Breed data not found."

    dataset = response.json()

    # Modify prompt to allow multiple categories
    response = co.chat(
        model="command-r-plus",
        message=f"""
        Identify the user's intent based on the following valid categories.
        A user query may be related to multiple categories, including general poultry care.

        {json.dumps(valid_categories, indent=4)}

        User input: {user_input}

        Return ONLY a valid JSON output without extra words. Example:

        {{
            "intents": [
                {{"intent": "Disease Prevention and Health", "subcategory": "Vaccination_schedule"}}
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

        # Handle breed-related data
        if intent in dataset:
            if intent == "Disease Prevention and Health" and subcategory == "Vaccination_schedule":
                vaccination_data = dataset.get(intent, {}).get("vaccination_schedule", [])
                formatted_result = format_vaccination_schedule(vaccination_data)
            else:
                formatted_result = dataset.get(intent, {}).get(subcategory, dataset.get(intent, "No data available."))
            
            if isinstance(formatted_result, list):
                formatted_result = "\n".join(f"- {entry}" for entry in formatted_result)
            
            results.append(f"**{intent}**:\n{formatted_result}")

        # Handle general poultry care
        elif intent == "General Poultry Care":
            general_response = co.chat(
                model="command-r-plus",
                message=f"""
                The user asked a poultry-related question: {user_input}.
                Provide a clear and concise response relevant to poultry care.
                """,
                temperature=0.7
            )
            return general_response.text

    # If no relevant data found, check if it's unrelated to poultry
    if not results:
        return "I'm here to help with poultry care and breed-related queries. Your question seems to be outside this scope."

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
        k=90
    )

    return final_response.text

if __name__ == "__main__":
    print(get_response("Sasso", "what is a subcutaneous injection"))
