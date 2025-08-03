import os
import time
import google.genai as genai
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from embeddings import CustomGoogleGenerativeAIEmbeddings
from typing import List

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Define the paths for the source documents and the persistent ChromaDB database.
SOURCE_DIRECTORY = "source_docs"
PERSIST_DIRECTORY = "chroma_db"

# --- Main Ingestion Logic ---
def main():
    """Main function to run the ingestion process."""
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    # 1. Load Documents
    documents = []
    for filename in os.listdir(SOURCE_DIRECTORY):
        if filename.endswith('.pdf'):
            file_path = os.path.join(SOURCE_DIRECTORY, filename)
            try:
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
                print(f"Successfully loaded {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    if not documents:
        print("No PDF documents found in the source directory. Exiting.")
        return

    # 2. Split Documents into Chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(docs)} chunks.")

    # 3. Create Embeddings using the custom class
    print("Initializing custom Google Generative AI Embeddings...")
    embeddings = CustomGoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001") # can change to other models if needed, but this is also using the default set in embeddings.py

    # 4. Create and Persist the Vector Store in Batches
    print("Initializing Chroma database...")
    # Initialize the Chroma database with the embedding function and persist directory.
    db = Chroma(
        persist_directory=PERSIST_DIRECTORY, 
        embedding_function=embeddings
    )

    # Process documents in batches to avoid API timeouts
    batch_size = 20 # We can likely use a larger batch size now
    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i:i + batch_size]
        batch_texts = [doc.page_content for doc in batch_docs]
        
        print(f"Processing batch {i//batch_size + 1}/{(len(docs) + batch_size - 1)//batch_size}...")
        
        # Add documents to the database
        db.add_documents(documents=batch_docs)
        
        # Small delay to respect potential rate limits
        time.sleep(1) 

    print("\nVector store created and updated successfully!")
    print(f"Total vectors in store: {db._collection.count()}")

if __name__ == "__main__":
    main()
