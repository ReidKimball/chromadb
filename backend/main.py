"""Main FastAPI application for the Wonder Sciences demo backend.

This file initializes the FastAPI application, configures CORS middleware, and defines
the API endpoints for handling chat interactions and retrieving AI prompts.

Attributes:
    app (FastAPI): The main FastAPI application instance.
    PROMPTS_DIR (str): The directory where AI system prompts are stored.
"""
import os
from fastapi import FastAPI, HTTPException  # Core FastAPI framework and exception handling
from fastapi.middleware.cors import CORSMiddleware  # Middleware for handling Cross-Origin Resource Sharing
from pydantic import BaseModel, Field  # For data validation and settings management
from typing import List, Dict, Optional  # Python's standard typing library
import re  # Regular expression library for parsing AI responses

# Third-Party Libraries
from dotenv import load_dotenv  # For loading environment variables from a .env file
from langchain_google_genai import ChatGoogleGenerativeAI  # Google Generative AI chat models
from langchain.schema import HumanMessage, SystemMessage, AIMessage  # LangChain schema for message types

# Load environment variables from .env file
load_dotenv()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Wonder Sciences Demo API",
    version="1.0.0",
    description="API for the Wonder Sciences AI chat demo, powered by FastAPI and LangChain."
)

# --- CORS Middleware Configuration ---
# This allows the frontend application to communicate with this backend API.
origins = [
    "http://localhost:3000",  # Local React development server
    "https://wsdemo-app-165871915889.us-central1.run.app",  # Deployed frontend application
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Whitelisted origins
    allow_credentials=True, # Allow cookies to be sent
    allow_methods=["*"],    # Allow all HTTP methods
    allow_headers=["*"],    # Allow all request headers
)

# --- Constants ---
PROMPTS_DIR = "ai_prompts"  # Directory for storing system prompt files

# --- Pydantic Models ---

class ChatMessage(BaseModel):
    """Represents a single message in the chat history.

    Attributes:
        role (str): The role of the message sender ('user' or 'assistant').
        content (str): The text content of the message.
    """
    role: str = Field(..., description="The role of the message sender, e.g., 'user' or 'assistant'.")
    content: str = Field(..., description="The text content of the message.")

class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    system_prompt: str = Field(..., description="The system prompt to guide the AI's behavior.")
    system_prompt_filename: str = Field(..., description="The filename of the system prompt being used.")
    history: List[ChatMessage] = Field(..., description="The chat history between the user and the assistant.")
    user_message: str = Field(..., description="The user's latest message.")
    model_name: Optional[str] = Field(default=None, description="The specific Gemini model to use for the chat.")

class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    reply: str = Field(..., description="The AI's response to the user's message.")
    analysis: str = Field(..., description="The AI's internal analysis of the conversation.")

# --- API Endpoints ---

@app.get("/api/prompts", summary="Get Available Prompts", tags=["Prompts"])
async def get_prompts():
    """Returns a list of available system prompt files from the `ai_prompts` directory."""
    return [f for f in os.listdir(PROMPTS_DIR) if f.endswith('.md')]

@app.get("/api/prompts/{prompt_name}", summary="Get Prompt Content")
def get_prompt_content(prompt_name: str):
    """Fetches the content of a specific system prompt file.

    Args:
        prompt_name (str): The filename of the prompt to retrieve.

    Returns:
        dict: A dictionary containing the content of the file, or an error
              message if the file is not found.
    """
    file_path = os.path.join(PROMPTS_DIR, prompt_name)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/models", tags=["Models"])
async def get_models():
    """Returns a list of available Gemini models."""
    # In a real-world scenario, this could be read from a config file
    # or an environment variable, but is hardcoded here for simplicity.
    available_models = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]
    return {"models": available_models}

@app.post("/api/chat", response_model=ChatResponse, description="Handles the chat interaction.", tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Receives a chat request, communicates with the Gemini API, and returns the AI's response.

    This endpoint orchestrates the conversation by:
    1.  Constructing a message history from the request.
    2.  Selecting the appropriate Gemini model (either from the request or the environment variable).
    3.  Invoking the model with the chat history and system prompt.
    4.  Parsing the response to separate the user-facing reply from the private analysis.
    5.  Returning the reply and analysis to the frontend.
    """
    # Use the model from the request, or fall back to the environment variable
    model_name = request.model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

    # Initialize the ChatGoogleGenerativeAI model
    llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=os.getenv("GEMINI_API_KEY"))

    # Construct the message history for the model
    messages = [SystemMessage(content=request.system_prompt)]
    for msg in request.history:
        if msg.role == 'user':
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == 'assistant':
            messages.append(AIMessage(content=msg.content))
    
    messages.append(HumanMessage(content=request.user_message))

    # --- LLM Invocation ---
    response = llm.invoke(messages)
    full_response_content = response.content

    # For debugging purposes, print the full raw response from the AI
    print("--- Full AI Response ---")
    print(full_response_content)
    print("-------------------------")

    # --- Response Parsing ---
    # Extract the AI's internal analysis and the user-facing reply
    analysis_content = ""
    user_reply = full_response_content

    # Use regex to find and extract content within <AI_ANALYSIS> tags
    analysis_match = re.search(r'<AI_ANALYSIS>(.*?)</AI_ANALYSIS>', full_response_content, re.DOTALL)
    if analysis_match:
        print("Found <AI_ANALYSIS> tags.")
        analysis_content = analysis_match.group(1).strip()
        # Remove the analysis part from the user-facing reply
        user_reply = re.sub(r'<AI_ANALYSIS>.*?</AI_ANALYSIS>', '', user_reply, flags=re.DOTALL).strip()
    else:
        print("Did not find <AI_ANALYSIS> tags.")

    # For debugging purposes, print the parsed components
    print(f"\n--- Extracted Analysis ---\n{analysis_content}")
    print(f"\n--- Cleaned User Reply ---\n{user_reply}\n")

    return {"reply": user_reply, "analysis": analysis_content}
