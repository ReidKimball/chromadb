import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- Setup ---
# Load environment variables from .env file
load_dotenv()

print("Attempting to configure Google API...")

# Configure the API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

genai.configure(api_key=api_key)

print("API configured successfully.")

# --- API Call ---
try:
    print("Attempting to embed content...")
    
    # The text to embed
    text_to_embed = "This is a simple test."
    
    # The model to use
    model = "models/gemini-embedding-001" # Note: The official library uses 'embedding-001', not 'gemini-embedding-001'
    
    # Make the API call
    result = genai.embed_content(model=model, content=text_to_embed)
    
    # --- Verification ---
    # Check if we received an embedding and print a success message
    if result['embedding']:
        print("\nSUCCESS! The API call was successful.")
        print(f"Received an embedding with {len(result['embedding'])} dimensions.")
    else:
        print("\nFAILURE! The API call did not return an embedding.")
        print(f"API Response: {result}")

except Exception as e:
    print(f"\nAn error occurred: {e}")
