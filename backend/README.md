# Project Plan: RAG Chat Application with ChromaDB

This document outlines the plan to build a Retrieval-Augmented Generation (RAG) chat application using a persistent ChromaDB database, designed for deployment on Google Cloud Run.

## Architecture

The application follows a stateless design suitable for serverless environments.

1.  **Ingestion Script (`ingest.py`):** A local Python script that runs **once** to process source documents (e.g., PDFs) and create a persistent, on-disk ChromaDB database in a local folder.

2.  **Backend (Python/FastAPI):** A stateless FastAPI application that serves the chat API. It is packaged in a Docker container that includes the pre-built ChromaDB database. The database is treated as a read-only asset.

3.  **Frontend (Next.js):** A web-based chat interface that communicates with the backend API.

## Deployment Workflow

1.  **Local Ingestion:**
    *   Place all source PDF documents into a designated folder (e.g., `source_documents`).
    *   Run the `ingest.py` script locally.
    *   This script reads the PDFs, chunks the text, generates embeddings, and saves the final vector database into a new directory (e.g., `chroma_db`).

2.  **Docker Build:**
    *   The `backend/Dockerfile` is configured to `COPY` the entire `chroma_db` folder into the Docker image during the build process.
    *   This "bakes" the database into the image, making the resulting container self-contained and ready for stateless deployment.

3.  **Deployment to Google Cloud Run:**
    *   Build the Docker image.
    *   Push the image to a container registry (e.g., Google Artifact Registry).
    *   Deploy the image to Google Cloud Run.

## Development Steps

1.  **Setup Backend Environment:** Update `requirements.txt` with necessary libraries and install them.
2.  **Create Ingestion Script (`ingest.py`):** Write the logic to find, process, and store documents in a persistent ChromaDB instance.
3.  **Update Backend Application (`main.py`):** Refactor the main application to connect to the pre-built, on-disk database and serve chat requests.
4.  **Update Dockerfile:** Add the `COPY` instruction to include the database in the image.
5.  **Update Frontend:** Simplify the UI by removing the file upload components, as the database is now pre-loaded.
