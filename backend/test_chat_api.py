import requests
import json

# The URL of the FastAPI endpoint
URL = "http://127.0.0.1:8000/api/chat"

# The header to specify that we are sending JSON
headers = {
    "Content-Type": "application/json"
}

# The data payload for the POST request
# This needs to match the ChatRequest Pydantic model in main.py
chat_request_data = {
    "system_prompt": "You are a helpful and friendly AI assistant specializing in dietary information. Your name is Nutri-Chat. You must answer user questions based *only* on the context provided. After your user-facing reply, you MUST include a special <AI_ANALYSIS> block. In this block, you will 'think out loud'. First, state which specific sentences from the context you used to form your answer. Second, explain your reasoning step-by-step. Third, state your confidence level (High, Medium, or Low). If the context does not contain the answer, you must state that and explain why the provided context is insufficient.",
    "system_prompt_filename": "SCD_Diet.md",
    "diet": "SCD",  # The new required field for metadata filtering
    "history": [],
    "user_message": "is spirulina allowed?",
    "model_name": "gemini-2.5-flash-lite" # Optional: specify a model
}

print(f"Sending POST request to {URL}...")
print("--- Request Payload ---")
print(json.dumps(chat_request_data, indent=2))
print("-----------------------\n")

try:
    # Make the POST request
    response = requests.post(URL, headers=headers, data=json.dumps(chat_request_data))

    # Check if the request was successful
    response.raise_for_status()  # This will raise an exception for HTTP errors (4xx or 5xx)

    # Parse the JSON response
    response_data = response.json()

    print("--- Server Response (SUCCESS) ---")
    print(f"Status Code: {response.status_code}")
    print(f"AI Reply: {response_data.get('reply')}")
    print(f"AI Analysis: {response_data.get('analysis')}")
    print("----------------------------------\n")

except requests.exceptions.RequestException as e:
    print(f"--- Server Response (ERROR) ---")
    print(f"An error occurred: {e}")
    print("-------------------------------\n")
