# Junior Developer's Guide to Building a RAG Ingestion Pipeline

This document is a primer on how we built the data ingestion pipeline for our RAG (Retrieval-Augmented Generation) chat application. It covers the core concepts, technology choices, and the lessons learned from debugging API changes.

## 1. The Goal: A Smart, Context-Aware Chatbot

Our objective is to create a chatbot that can answer questions about specific dietary information. To do this, it needs access to a knowledge base. The RAG pattern allows us to fetch relevant information from our database and provide it to the AI as context, leading to more accurate and relevant answers.

## 2. The Tech Stack

- **Backend Framework**: `FastAPI` - A modern, fast web framework for building APIs with Python.
- **Vector Database**: `ChromaDB` - An open-source embedding database that makes it easy to store and query vector embeddings locally.
- **AI & Embeddings**: `Google Gemini API` - Used for both generating the embeddings (turning text into numerical vectors) and for the final chat completion.
- **Orchestration**: `LangChain` - A library that helps chain together the different components (like the database and the AI model).
- **Environment**: `python-dotenv` - For managing environment variables like API keys securely.

## 3. The Core: Data Ingestion (`ingest.py`)

The most critical part of any RAG system is the quality of the data it retrieves. Here's how we built our ingestion pipeline:

### Start with Clean, Structured Data

We started with a structured `foods.json` file instead of unstructured PDFs. This was a key decision.

- **Why JSON?** It provides clean, pre-organized data. Each food item is a distinct entry with clear fields like `food_name`, `allowed`, `diet_code`, and `notes`.
- **Benefit**: This eliminates the complex and often error-prone step of parsing, cleaning, and splitting text from a format like PDF.

### Use Metadata for Filtering

Instead of creating a separate database for each diet, we store all food items in one unified database. We use **metadata** to distinguish them.

When creating each LangChain `Document`, we attach metadata to it:

```python
# From ingest.py
doc = Document(
    page_content=descriptive_string,
    metadata={"diet_code": item['diet_code'], "allowed": item['allowed']}
)
```

This allows us to perform filtered queries later, such as "find all allowed foods where `diet_code` is 'SCD'".

## 4. The Engine: Custom Gemini Embeddings (`embeddings.py`)

To turn our text into vectors, we needed to interact with the Google Gemini API. The API libraries updated during our development, which required us to adapt.

### Key Lessons & Correct Usage:

1.  **Environment Variable**: Your API key must be stored in a `.env` file and loaded into the environment. The key should be named `GEMINI_API_KEY`.

2.  **API Client Initialization**: The modern `google-genai` library does **not** use `genai.configure()`. Instead, you instantiate a client, which automatically finds the API key in your environment.

    ```python
    # Correct way to initialize
    import os
    from google import genai

    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY not found...")
    self.client = genai.Client()
    ```

3.  **Calling the Embedding Endpoint**: The function call is made on the `client.models` object.

    ```python
    # Correct function call
    result = self.client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=texts # Note: it's 'contents' (plural)
    )
    ```

4.  **Handling the API Response**: The API does not return a simple list of numbers. It returns a list of `ContentEmbedding` objects. You must extract the numerical vector from the `.values` attribute of each object.

    ```python
    # Correct way to extract the vectors
    embeddings = [e.values for e in result.embeddings]
    return embeddings
    ```

## 5. The Database: Storing Vectors with ChromaDB

ChromaDB makes creating and persisting the vector store simple.

- **Batching**: We process documents in batches to avoid overwhelming the API and to manage memory efficiently.
- **Creation & Persistence**: `Chroma.from_documents()` takes our LangChain `Document` objects and an embedding function, and handles the entire process of creating vectors and storing them. By providing a `persist_directory`, the database is saved to disk.

```python
# From ingest.py
db = Chroma.from_documents(
    documents=batch_docs,
    embedding=embeddings, # Our custom embedding class
    persist_directory="./chroma_db"
)
db.persist()
```

This creates a `chroma_db` folder containing the complete, ready-to-use vector database.
