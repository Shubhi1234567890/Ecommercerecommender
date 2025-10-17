import random
from sqlalchemy.orm import Session
from sqlalchemy import func
from .db import Product, Interaction, DB_ENGINE # Import DB components

# --- Configuration ---
MAX_RECOMMENDATIONS = 3
INTERACTION_WEIGHTS = {
    'purchase': 3,
    'like': 2,
    'view': 1
}

def get_recommendations(user_id: str):
    """
    Generates a list of hybrid recommendations (Category affinity + Popularity)
    and prepares the context for the LLM explanation.
    """
    session = Session(bind=DB_ENGINE)
    recommendations = {} # Use a dictionary to avoid recommending the same product twice

    try:
        # --- 1. Identify User History and Favorite Category ---

        # Get all of the user's interactions and calculate affinity scores
        user_interactions = session.query(Interaction).filter(Interaction.user_id == user_id).all()
        user_purchased_ids = {i.product_id for i in user_interactions if i.interaction_type == 'purchase'}

        category_scores = {}
        for interaction in user_interactions:
            # Find the product's category (requires joining or a secondary query, 
            # but for simplicity, we'll query the product directly here)
            product = session.query(Product).filter(Product.product_id == interaction.product_id).first()
            if product:
                category = product.category
                score = INTERACTION_WEIGHTS.get(interaction.interaction_type, 0)
                category_scores[category] = category_scores.get(category, 0) + score

        # Find the top category
        if category_scores:
            favorite_category = max(category_scores, key=category_scores.get)
            user_affinity_summary = f"User has strong affinity ({category_scores[favorite_category]} score) for the '{favorite_category}' category based on past interactions."
        else:
            favorite_category = None
            user_affinity_summary = "User is a new customer with limited history, defaulting to popular products."


        # --- 2. Content-Based Recommendation (Category Affinity) ---
        if favorite_category:
            category_recs = session.query(Product).filter(
                Product.category == favorite_category,
                ~Product.product_id.in_(user_purchased_ids) # Exclude already purchased items
            ).order_by(func.random()).limit(MAX_RECOMMENDATIONS).all()

            for rec in category_recs:
                if len(recommendations) < MAX_RECOMMENDATIONS:
                    recommendations[rec.product_id] = {
                        "product": rec,
                        "reason_type": "Content/Affinity",
                        "user_activity": user_affinity_summary,
                    }

        # --- 3. Popularity Recommendation (Best Sellers) ---
        
        # Get global purchase counts
        purchase_counts = session.query(
            Interaction.product_id, 
            func.count(Interaction.product_id).label('count')
        ).filter(
            Interaction.interaction_type == 'purchase',
            ~Interaction.product_id.in_(user_purchased_ids) # Exclude already purchased items
        ).group_by(
            Interaction.product_id
        ).order_by(
            func.max('count').desc() # Sort by purchase count
        ).limit(MAX_RECOMMENDATIONS).all()

        # Fetch the product objects for the best sellers
        best_seller_ids = [item[0] for item in purchase_counts]
        best_sellers = session.query(Product).filter(
            Product.product_id.in_(best_seller_ids)
        ).all()
        
        # Add best sellers until we hit the limit
        for rec in best_sellers:
            if len(recommendations) < MAX_RECOMMENDATIONS:
                recommendations[rec.product_id] = {
                    "product": rec,
                    "reason_type": "Popularity/Best-Seller",
                    "user_activity": f"This item is globally popular, ranking among the top {len(best_seller_ids)} purchased products.",
                }

        # --- 4. Final Formatting ---
        # Convert the dictionary of recommendations to a list and truncate to MAX_RECOMMENDATIONS
        final_recs = list(recommendations.values())[:MAX_RECOMMENDATIONS]

        if not final_recs and not user_interactions:
            # Fallback for users with no history and no popular items found (or small data set)
            # Pick the first MAX_RECOMMENDATIONS products as a default
            default_prods = session.query(Product).order_by(Product.product_id).limit(MAX_RECOMMENDATIONS).all()
            for prod in default_prods:
                 final_recs.append({
                    "product": prod,
                    "reason_type": "Default/New User",
                    "user_activity": "No interaction history found; showing highly-rated introductory items.",
                })


        return final_recs

    except Exception as e:
        print(f"Error during recommendation generation: {e}")
        return []
        
    finally:
        session.close()
