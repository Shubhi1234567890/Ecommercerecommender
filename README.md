📦 AI-Powered Recommendation Engine (FastAPI & Gemini)

This project implements a personalized recommendation system using a FastAPI backend, a relational database (SQLite/SQLAlchemy), and leverages the Gemini API for advanced, context-aware suggestions.

⚙️ Architecture Overview

The system utilizes a simple client-server architecture:

Data Ingestion: Mock product and interaction data (data/) is loaded into a persistent SQLite database (via db.py).

Core Logic: The recommender.py module processes user interactions to generate basic recommendations (e.g., collaborative filtering or content-based matching).

Intelligent Refinement: The llm_service.py uses the Gemini API to take the base recommendations and refine them based on user context or current trends, providing personalized, natural language-driven product descriptions or suggestions.

API Gateway: main.py handles all routing and exposes endpoints (e.g., /recommend/user_id).

🛠️ Setup and Installation

Prerequisites

Python 3.9+

A Gemini API Key (set as an environment variable)

Installation Steps

Clone the Repository:

git clone [Your Repository URL]
cd [repository-name]


Install Dependencies:

pip install -r requirements.txt


Set Environment Variables:

export GEMINI_API_KEY="YOUR_API_KEY_HERE"


Run the Application:

# Uvicorn is the ASGI server used by FastAPI
uvicorn app.main:app --reload


The API will be available at https://aistudio.google.com/api-keys. You can view the interactive documentation at http://127.0.0.1:8000/docs.

📂 File Structure Breakdown

File

Role

Key Functionality

app/main.py

API Entry Point

Defines /recommend and /products endpoints. Orchestrates calls between db.py, recommender.py, and llm_service.py.

app/db.py

Data Layer

Sets up the SQLite database, defines SQLAlchemy models (Products, Users, Interactions), and loads initial data from data/products.csv.

app/recommender.py

Recommendation Core

Contains the non-LLM logic, such as filtering products or calculating similarity scores based on historical interactions.

app/llm_service.py

AI Interface

Handles all communication with the Gemini API for advanced recommendation explanations or creative suggestion generation.

data/

Data Storage

Contains mock datasets necessary for populating the database.
