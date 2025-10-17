# Hybrid LLM-Powered E-commerce Recommender API

This project implements a personalized product recommendation API built with **FastAPI**, utilizing a hybrid recommendation strategy (Content-Based and Popularity) and leveraging the **Gemini API** to generate personalized, contextual explanations for each recommendation.

## Features

* **Hybrid Recommendation Logic:** Combines a user's purchase history (Content-Based focusing on their favorite category) with global best-selling products (Popularity-Based).
* **LLM Explanation:** Uses the Gemini API to generate a unique, human-readable explanation for *why* each product was recommended, providing transparency and increasing user trust.
* **Scalable API:** Built on FastAPI for high performance and automatic documentation (Swagger UI).
* **Persistent Storage:** Uses SQLite and SQLAlchemy to manage product and user interaction data.

---

## Project Structure

This project has a simple structure designed for a small, functional API service:

.├── app/│   ├── main.py             # FastAPI application entry point and routing│   ├── db.py               # Database setup, SQLAlchemy models, and initial data loading│   ├── recommender.py      # Core recommendation logic│   └── llm_service.py      # Handles interaction with the Gemini API├── data/│   ├── products.csv        # Mock product data│   └── interactions.csv    # Mock user activity (purchases, views, likes)├── requirements.txt        # Python package dependencies└── README.md               # This documentation file
---

## Setup and Installation

### 1. Prerequisites

* Python 3.8+
* A **Gemini API Key** from Google AI Studio.

### 2. Environment Setup

Clone the repository and install dependencies:

```bash
# Install required Python packages

pip install -r requirements.txt

3. Configure the Gemini API KeyYou must provide your Gemini API Key to the application. You should have already done this in app/llm_service.py by replacing the placeholder with your actual key.4. Run the ApplicationStart the FastAPI server using 

Uvicorn:Bash uvicorn app.main:app--reload

The application will start at http://127.0.0.1:8000.API UsageThe API provides one main endpoint for fetching personalized recommendations.Get RecommendationsGET /api/v1/recommend/{user_id}ParameterTypeDescriptionuser_idPath (string)The ID of the user (e.g., U101, U102)Example Request:Bashcurl -X 'GET' '[http://127.0.0.1:8000/api/v1/recommend/U101](http://127.0.0.1:8000/api/v1/recommend/U101)' -H 'accept: application/json'

You can also test the endpoint directly using the Swagger UI available at: http://127.0.0.1:8000/docs