# How This AI Works: A Guide for Junior Developers

This document explains the architecture of our Retrieval-Augmented Generation (RAG) system. RAG is a powerful technique that allows a Large Language Model (LLM) like Google's Gemini to answer questions using a specific knowledge base, rather than relying solely on its general training data.

Our system has two distinct phases:

1.  **Offline Indexing**: A one-time process where we convert our knowledge base (text documents) into a searchable vector database.
2.  **Online Serving**: A real-time process where the FastAPI backend uses the vector database to answer user questions.

---

## 1. Offline Indexing: Building the Knowledge Base

Before the API can answer any questions, we must first process our source documents. This is done locally using a script (e.g., `build_database.py`).

**What happens in this step?**

1.  **Load Documents**: The script reads all the text files from our knowledge base.
2.  **Create Embeddings**: Each document (or chunk of a document) is fed into an **embedding model** (like `gemini-embedding-001`). This model converts the text into a high-dimensional vector—a long list of numbers that represents the text's semantic meaning. Similar pieces of text will have vectors that are mathematically close to each other.
3.  **Store in ChromaDB**: These vectors, along with their original text and some metadata (like a `diet_code`), are stored in a **vector database**. We use ChromaDB for this. The result is a folder named `chroma_db` that contains the complete, searchable knowledge base.

> **Key Takeaway**: The `chroma_db` directory is a pre-built, portable representation of our entire knowledge base. This expensive embedding process only happens once, not every time the server starts.

---

## 2. Online Serving: Answering a User's Question

This is what our FastAPI backend (`main.py`) does. When a user sends a message to the chatbot, the backend orchestrates a multi-step process to generate an accurate, context-aware answer.

Here’s the journey of a single user request through the `/api/chat` endpoint:

### Step A: Server Startup

When the application starts (e.g., on Google Cloud Run), it does two quick things:

1.  `embeddings = CustomGoogleGenerativeAIEmbeddings()`: It creates an object that knows how to use the *same embedding model* we used during indexing.
2.  `vector_store = Chroma(...)`: It loads the pre-built `chroma_db` from disk into memory. This is fast because it's just reading existing files, not creating new embeddings.

### Step B: A User Sends a Message

The frontend sends a request to `/api/chat` containing the user's message, chat history, and the selected diet (`'SCD'`, `'GAPS'`, etc.).

### Step C: Retrieve Relevant Documents (The "Retrieval" in RAG)

This is the core of the "retrieval" part.

1.  **Embed the User's Question**: The user's message is converted into a vector using the same embedding model from startup.
2.  **Search the Vector Store**: ChromaDB takes this new vector and searches for the most similar vectors in its database (a "nearest neighbor" search). It also filters the results to only include documents whose metadata matches the requested `diet_code`.
3.  **Collect the Results**: The retriever returns a list of the most relevant text chunks from the original knowledge base.

```python
# main.py

# Create a retriever with a metadata filter
retriever = vector_store.as_retriever(
    search_kwargs={'filter': {'diet_code': request.diet}}
)

# Find documents relevant to the user's message
relevant_docs = retriever.invoke(request.user_message)
```

### Step D: Augment the Prompt (The "Augmented" in RAG)

Now that we have the most relevant information, we don't just ask the LLM the user's question directly. Instead, we give it **context**.

We construct a special **system prompt** that looks like this:

```
You are a helpful AI assistant. Use the following context to answer the user's question.

<CONTEXT>
[Content of the first relevant document...]
---
[Content of the second relevant document...]
</CONTEXT>

User's original question: [The user's message here]
```

This `final_system_prompt` now contains both the original instructions and the specific, relevant information needed to answer the current question.

### Step E: Generate the Answer (The "Generation" in RAG)

Finally, we send the complete package—the augmented system prompt and the full conversation history—to the LLM (e.g., `gemini-2.5-pro`).

```python
# main.py
response = llm.invoke(messages) # 'messages' includes the augmented prompt
```

Because the LLM has the retrieved context right in front of it, it can generate a factually accurate answer that is grounded in our specific knowledge base. It's not just using its general knowledge; it's using the information we just gave it.

### Step F: Return the Response

The LLM's reply is sent back to the frontend to be displayed to the user.

---

## Summary of Concepts

*   **Embeddings**: Numerical representations of text that capture semantic meaning.
*   **Vector Database**: A database optimized for storing and searching vectors (e.g., ChromaDB).
*   **Retrieval-Augmented Generation (RAG)**: The process of retrieving relevant information from a knowledge base and providing it to an LLM as context to generate a more accurate and informed answer.
