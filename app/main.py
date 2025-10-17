from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import OperationalError
from .db import init_db
from .recommender import get_recommendations
from .llm_service import generate_explanation

# --- Application Setup ---

app = FastAPI(
    title="E-commerce Recommender API",
    description="Provides personalized product recommendations with LLM-generated explanations.",
    version="1.0.0"
)

# Initialize the database on startup
# Note: In a production environment, this would run separately.
# We run it here for simplicity in this self-contained project.
try:
    init_db()
except OperationalError as e:
    print(f"FATAL DB ERROR: Could not connect or initialize database. Check data files. {e}")
except Exception as e:
    print(f"FATAL STARTUP ERROR: {e}")

# --- API Endpoint ---

@app.get("/api/v1/recommend/{user_id}", tags=["Recommendations"])
async def get_user_recommendations(user_id: str):
    """
    Returns a list of 3 personalized product recommendations,
    each enriched with an LLM-generated explanation.
    """
    print(f"Processing request for User ID: {user_id}")
    
    # 1. Get raw recommendations and context from the core engine
    raw_recs = get_recommendations(user_id)
    
    if not raw_recs:
        raise HTTPException(
            status_code=404, 
            detail="No products found or recommendation logic failed to produce results."
        )

    final_recs = []
    
    # 2. Loop through results and enrich each with the LLM explanation
    for rec in raw_recs:
        
        # Call the LLM service to generate the personalized text
        explanation = generate_explanation(
            product=rec["product"],
            reason_type=rec["reason_type"],
            user_activity=rec["user_activity"]
        )
        
        # Structure the final output
        product = rec["product"]
        final_recs.append({
            "product_id": product.product_id,
            "product_name": product.name,
            "category": product.category,
            "price": product.price,
            "llm_explanation": explanation, # The key deliverable
            "internal_reason": rec["reason_type"] # For debugging/transparency
        })

    return {
        "user_id": user_id, 
        "recommendations": final_recs,
        "total_recommendations": len(final_recs)
    }
