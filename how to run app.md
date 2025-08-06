# How to Run This Application

This guide provides instructions on how to set up and run the application, which consists of a Python backend and a Next.js frontend.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Python](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/en/download/)

## Backend Setup

1.  **Open a new terminal** (PowerShell is recommended).

2.  **Navigate to the backend directory:**
    ```powershell
    cd c:\Users\Reid\Documents\Programming\chromadb\backend
    ```

3.  **Activate the Python virtual environment:**
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```
    Your terminal prompt should now be prefixed with `(.venv)`.

4.  **Install the required Python packages:**
    ```powershell
    pip install -r requirements.txt
    ```

5.  **Run the backend server:**
    ```powershell
    uvicorn main:app --reload
    ```
    The backend server should now be running, typically on port 8000.

## Frontend Setup

1.  **Open a second, separate terminal**.

2.  **Navigate to the frontend directory:**
    ```powershell
    cd c:\Users\Reid\Documents\Programming\chromadb\frontend
    ```

3.  **Install the required Node.js packages:**
    ```powershell
    npm install
    ```

4.  **Run the frontend development server:**
    ```powershell
    npm run dev
    ```

## Accessing the Application

Once both the backend and frontend servers are running, you can access the application by opening your web browser and navigating to:

[http://localhost:3000](http://localhost:3000)
