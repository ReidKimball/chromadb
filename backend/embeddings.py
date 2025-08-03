import os
import google.genai as genai
from dotenv import load_dotenv
from langchain.embeddings.base import Embeddings
from typing import List

# Load environment variables from .env file
load_dotenv()

class CustomGoogleGenerativeAIEmbeddings(Embeddings):
    """A custom embedding class that uses the google-genai library directly."""
    def __init__(self, model: str = "models/gemini-embedding-001"): # Default model
        self.model = model
        # In the new version, we create a client instance.
        # The client automatically uses the GEMINI_API_KEY from the environment.
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        self.client = genai.Client()

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Helper function to embed a list of texts."""
        try:
            # Call the embed_content method on the client's model object
            result = self.client.models.embed_content(model=self.model, contents=texts)
            # The API returns a list of ContentEmbedding objects. We need to extract the
            # raw list of floats from the .values attribute of each object.
            return [embedding.values for embedding in result.embeddings]
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
