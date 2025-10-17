import random
import pandas as pd
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base, Session
from datetime import datetime

# --- Configuration ---
DATABASE_NAME = "recommender.db"
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"

# Create the SQLAlchemy engine and base
DB_ENGINE = create_engine(DATABASE_URL)
Base = declarative_base()

# --- Database Models ---

class Product(Base):
    """Defines the schema for the product catalog."""
    __tablename__ = 'products'
    
    product_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    # The description field is crucial for the LLM to generate rich explanations
    description = Column(String, nullable=False)

    def __repr__(self):
        return f"<Product(id='{self.product_id}', name='{self.name}', category='{self.category}')>"

class Interaction(Base):
    """Defines the schema for user interaction data (view, like, purchase)."""
    __tablename__ = 'interactions'

    id = Column(String, primary_key=True, default=lambda: str(hash(datetime.now().microsecond + random.randint(1, 1000))))
    user_id = Column(String, index=True, nullable=False)
    product_id = Column(String, nullable=False, index=True)
    interaction_type = Column(String, nullable=False) # e.g., 'view', 'like', 'purchase'
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Interaction(user='{self.user_id}', product='{self.product_id}', type='{self.interaction_type}')>"


# --- Database Initialization Function ---

def init_db(engine=None):
    """
    Initializes the SQLite database, creates tables, and populates them
    with data from products.csv and interactions.csv.
    """
    if engine is None:
        engine = DB_ENGINE
        
    Base.metadata.create_all(engine)
    
    session = Session(bind=engine)
    
    # 1. Load Products Data
    try:
        products_df = pd.read_csv('data/products.csv')
        
        # Check if products are already loaded (simple check)
        if session.query(Product).count() == 0:
            print("Populating 'products' table...")
            
            # Map DataFrame columns to Product model attributes
            products_to_add = []
            for _, row in products_df.iterrows():
                product = Product(
                    product_id=row['product_id'],
                    name=row['name'],
                    category=row['category'],
                    price=row['price'],
                    description=row['description (for LLM)']
                )
                products_to_add.append(product)
            
            session.bulk_save_objects(products_to_add)
        else:
            print("'products' table already populated.")
    except FileNotFoundError:
        print("Error: data/products.csv not found. Cannot populate products.")
    except Exception as e:
        print(f"Error loading products: {e}")
        
    # 2. Load Interactions Data
    try:
        interactions_df = pd.read_csv('data/interactions.csv')
        
        # Check if interactions are already loaded
        if session.query(Interaction).count() == 0:
            print("Populating 'interactions' table...")
            
            interactions_to_add = []
            for _, row in interactions_df.iterrows():
                interaction = Interaction(
                    user_id=row['user_id'],
                    product_id=row['product_id'],
                    interaction_type=row['interaction_type'],
                    # Convert timestamp string to datetime object
                    timestamp=pd.to_datetime(row['timestamp']) 
                )
                interactions_to_add.append(interaction)

            session.bulk_save_objects(interactions_to_add)
        else:
            print("'interactions' table already populated.")
    except FileNotFoundError:
        print("Error: data/interactions.csv not found. Cannot populate interactions.")
    except Exception as e:
        print(f"Error loading interactions: {e}")
    
    session.commit()
    session.close()
    print("Database initialization complete.")

if __name__ == '__main__':
    # This allows direct testing of the DB setup
    init_db()
