import json, re, cohere, os, requests
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

system_public_url = os.getenv("PUBLIC_URL")

valid_categories = {
    "Feeding and Nutrition": ["Chick", "Grower", "Broiler", "Layer", "Supplementation", "Alternative_feeds"],
    "Housing and Environment": ["Space_per_bird", "Ventilation", "Temperature", "Humidity", "Biosecurity"],
    "Disease Prevention and Health": ["Common_diseases", "Vaccination_schedule", "Signs_of_illness", "Deworming"],
    "Breed Characteristics": ["Temperament", "Farming_suitability", "Climate_adaptability", "Special_needs"],
    "General Poultry Care": ["Injection_types", "Biosecurity_measures", "Common_treatments"],
    
    "Breed Physical Description": ["Body_Shape", "Feather_Color_Pattern", "Comb_Type", "Leg_Color_Features", 
                                   "Beak_Shape_Color", "Wattles_Earlobes", "Skin_Color", "Tail_Shape_Size"],

    "Breeding and Reproduction": ["Best_breeding_age", "Egg_production", "Brooding_requirements", "Incubation_methods"],
    "Productivity and Economics": ["Growth_rate", "Egg_laying", "Market_price", "Profit_maximization"],

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

def get_response(selected_breed, user_input, chat_history):
    for query in chat_history:
        if query["role"] == "USER":
            query["role"] = "User"
        elif query["role"] == "BOT":
            query["role"] = "Chatbot"

    # Fetch breed data dynamically
    response = requests.get(f"{system_public_url}/get_breed_data/{selected_breed}")

    if response.status_code != 200:
        return f"Error: No data available for the breed '{selected_breed}'. Please check the breed name."

    dataset = response.json()

    # Extract intent
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
        """,
        chat_history = chat_history
    )

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

    # If no intents are detected, check if the question is unrelated
    if not detected_intents:
        unrelated_query_check = co.chat(
            model="command-r-plus",
            message=f"""
            Determine if the user's question is related to poultry care or breed-specific knowledge.
            If it is not related, return this exact response: "UNRELATED_QUERY".
            Otherwise, return "RELATED_QUERY".
            
            User input: {user_input}
            """,
            chat_history=chat_history
        )

        if "UNRELATED_QUERY" in unrelated_query_check.text:
            return "I'm here to assist with poultry breeds and care. Your query seems unrelated."

        return "I couldn't determine the exact category of your question. Could you clarify?"

    # Retrieve relevant information for each detected category
    results = []
    for item in detected_intents:
        intent = item.get("intent", "Unknown")
        subcategory = item.get("subcategory", None)

        # Handle disease-specific vaccination schedule
        if intent == "Disease Prevention and Health" and subcategory == "Vaccination_schedule":
            vaccination_data = dataset.get(intent, {}).get("vaccination_schedule", [])

            # Extract possible disease name from user input
            known_diseases = [entry["Disease"].lower() for entry in vaccination_data]
            disease_queried = None

            for disease in known_diseases:
                if disease in user_input.lower():
                    disease_queried = disease
                    break

            if disease_queried:
                # Filter vaccination schedule for the specific disease
                filtered_schedule = [
                    entry for entry in vaccination_data if entry["Disease"].lower() == disease_queried
                ]
                if filtered_schedule:
                    formatted_result = format_vaccination_schedule(filtered_schedule)
                else:
                    formatted_result = f"No vaccination data found for {disease_queried}."
            else:
                formatted_result = format_vaccination_schedule(vaccination_data)

            results.append(f"**Vaccination Schedule**:\n{formatted_result}")

        elif intent in dataset:
            formatted_result = dataset.get(intent, {}).get(subcategory, dataset.get(intent, "No data available."))

            if isinstance(formatted_result, list):
                formatted_result = "\n".join(f"- {entry}" for entry in formatted_result)

            results.append(f"**{intent}**:\n{formatted_result}")

    # If no relevant data found
    if not results:
        return f"I'm here to assist with {selected_breed} breed information and poultry care. I couldn't find relevant data for your question."

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
        chat_history=chat_history,
        temperature=0.8,
        k=90
    )

    return final_response.text



if __name__ == "__main__":
    print(get_response("Sasso", "what is a subcutaneous injection"))
