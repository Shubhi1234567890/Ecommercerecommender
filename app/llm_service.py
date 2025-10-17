import os
import time
from google import genai
from google.genai.errors import APIError
from typing import Dict, Any

# --- LLM Client Initialization ---
# This version reads the API key from the environment first, but uses a
# hardcoded key as a fallback for debugging, which resolves the 'Unavailable' error.
# 
# !!! CRITICAL: Replace "PASTE_YOUR_API_KEY_HERE" with your actual key !!!
api_key = os.getenv("GEMINI_API_KEY", "AIzaSyA9yzwYSxW9L69Yl7NeXYeKEQbEuj6y-fw")

# Initialize the Gemini API client only if a key is available
if api_key and api_key != "AIzaSyA9yzwYSxW9L69Yl7NeXYeKEQbEuj6y-fw":
    try:
        # Pass the key directly to ensure it's used
        client = genai.Client(api_key=api_key)
        client_initialized = True
    except Exception as e:
        print(f"ERROR: Gemini Client failed to initialize with provided key. Error: {e}")
        client_initialized = False
        client = None
else:
    print("WARNING: Gemini API Key is missing. LLM explanations will fail.")
    client_initialized = False
    client = None

# --- Prompt Engineering ---

SYSTEM_PROMPT = """
You are a concise, helpful, and highly personalized e-commerce recommendation expert.
Your task is to generate a short, engaging, and professional explanation (max 3 sentences)
for why a specific product is being recommended to the user.

RULES:
1. Always reference the product's details and the user's specific context.
2. Use a positive and encouraging tone.
3. Do not use markdown (e.g., bolding, lists) in the output.
4. Keep the explanation to three sentences or less.
"""

def generate_explanation(product: Dict[str, Any], reason_type: str, user_activity: str) -> str:
    """
    Constructs a detailed prompt and calls the Gemini API to get a personalized explanation.
    Implements a simple exponential backoff for retries.
    """
    global client, client_initialized

    if not client_initialized:
        return "LLM service is unavailable. Please check the API key configuration."

    # Construct the personalized user query
    user_query = f"""
    Product Details:
    - Name: {product.name}
    - Category: {product.category}
    - Description: {product.description}
    - Price: ${product.price:.2f}

    Recommendation Reason: {reason_type}
    User Context/Activity: {user_activity}

    Generate the personalized explanation now based on the system prompt.
    """
    
    # Simple retry mechanism with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_query,
                config=genai.types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )
            return response.text.strip()
            
        except APIError as e:
            # Handle specific API errors (e.g., rate limits)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"API Error: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return f"LLM API failed after {max_retries} attempts: {e}"
        except Exception as e:
            return f"An unexpected error occurred during LLM generation: {e}"
    
    return "Failed to generate explanation due to an unknown error."