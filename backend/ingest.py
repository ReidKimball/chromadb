import os
import time
import google.genai as genai
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.base import Embeddings
from typing import List

# Load environment variables from .env file
load_dotenv()

# --- Custom Embedding Class ---
class CustomGoogleGenerativeAIEmbeddings(Embeddings):
    """A custom embedding class that uses the google-generativeai library directly."""
    def __init__(self, model: str = "models/embedding-001"):
        self.model = model
        # Configure the API key at initialization
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        genai.configure(api_key=api_key)

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Helper function to embed a list of texts, with retries."""
        try:
            result = genai.embed_content(model=self.model, content=texts)
            return result['embedding']
        except Exception as e:
            print(f"An error occurred during embedding: {e}")
            return [[] for _ in texts] # Return empty embeddings on failure

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents, handling batching and retries."""
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query."""
        return self._embed([text])[0]

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
    embeddings = CustomGoogleGenerativeAIEmbeddings(model="models/embedding-001")

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
