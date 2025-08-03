import os
import time
import json
import shutil
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from embeddings import CustomGoogleGenerativeAIEmbeddings

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Define the paths for the source JSON file and the persistent ChromaDB database.
SOURCE_DATA_FILE = os.path.join("source_data", "meadow_mentor.therapeutic-diet-foods.json")
PERSIST_DIRECTORY = "chroma_db"

# --- Main Ingestion Logic ---
def main():
    """Main function to run the ingestion process from a JSON file."""
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    # 1. Clean up old database directory
    if os.path.exists(PERSIST_DIRECTORY):
        print(f"Removing old database from '{PERSIST_DIRECTORY}'")
        shutil.rmtree(PERSIST_DIRECTORY)

    # 2. Load and Process JSON Data
    try:
        with open(SOURCE_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{SOURCE_DATA_FILE}' was not found. Please ensure it exists.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{SOURCE_DATA_FILE}' is not a valid JSON file.")
        return

    documents = []
    print(f"Processing {len(data)} food items from the JSON file...")
    for item in data:
        # Construct the descriptive string for embedding
        allowed_status = "allowed" if item.get('allowed', False) else "not allowed"
        note = item.get('note')
        
        page_content = f"Diet: {item.get('diet_code', 'N/A')}. " \
                       f"Food: {item.get('food_name', 'N/A')}. " \
                       f"Status: {allowed_status}."
        if note and note.strip():
            page_content += f" Note: {note}"

        # Create metadata, ensuring all values are of a supported type
        metadata = {
            "source": SOURCE_DATA_FILE,
            "food_name": str(item.get('food_name', 'N/A')),
            "diet_code": str(item.get('diet_code', 'N/A')),
            "allowed": bool(item.get('allowed', False))
        }
        
        # Create a LangChain Document
        doc = Document(page_content=page_content.strip(), metadata=metadata)
        documents.append(doc)

    if not documents:
        print("No documents were created from the JSON file. Exiting.")
        return
    
    print(f"Successfully created {len(documents)} documents to be embedded.")

    # 3. Create Embeddings using the custom class
    print("Initializing custom Google Generative AI Embeddings...")
    embeddings = CustomGoogleGenerativeAIEmbeddings() # uses default model in embeddings.py

    # 4. Create and Persist the Vector Store in Batches
    print(f"Creating new vector store in '{PERSIST_DIRECTORY}'...")
    
    # Process documents in batches to add to ChromaDB
    batch_size = 50  # Adjust batch size as needed
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}...")
        
        if i == 0:
            # For the first batch, create the database
            db = Chroma.from_documents(
                documents=batch_docs,
                embedding=embeddings,
                persist_directory=PERSIST_DIRECTORY
            )
        else:
            # For subsequent batches, add to the existing database
            db.add_documents(documents=batch_docs)
        
        # Small delay to respect potential rate limits
        time.sleep(1)

    print("\nVector store created and updated successfully!")
    print(f"Total vectors in store: {db._collection.count()}")

if __name__ == "__main__":
    main()
