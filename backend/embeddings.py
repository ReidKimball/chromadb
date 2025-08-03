import os
import google.genai as genai
from dotenv import load_dotenv
from langchain.embeddings.base import Embeddings
from typing import List

# Load environment variables from .env file
load_dotenv()

class CustomGoogleGenerativeAIEmbeddings(Embeddings):
    """A custom embedding class that uses the google-genai library directly."""
    def __init__(self, model: str = "models/gemini-embedding-001"):
        self.model = model
        # Configure the API key at initialization
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        genai.configure(api_key=api_key)

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Helper function to embed a list of texts."""
        try:
            # Note: The 'content' parameter can be a single string or a list of strings.
            result = genai.embed_content(model=self.model, content=texts)
            return result['embedding']
        except Exception as e:
            print(f"An error occurred during embedding: {e}")
            # Return a list of empty lists, one for each text that failed.
            return [[] for _ in texts]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents."""
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query."""
        # The API expects a list, so we wrap the single text in a list
        # and then return the first (and only) embedding from the result.
        embedding_list = self._embed([text])
        return embedding_list[0] if embedding_list else []
