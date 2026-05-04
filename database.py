import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. DYNAMIC URL: Try to get the Supabase link from Render, otherwise use your local one
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Use your local database name 'mini_bank_db' here
    DATABASE_URL = "postgresql://postgres:raoinam7462@localhost/mini_bank_db"

# 2. RENDER FIX: Ensure the URL starts with 'postgresql://' instead of 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. SETUP ENGINE: Now we create only ONE engine and ONE SessionLocal
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. TABLE CREATOR: This will run on Supabase automatically
def create_tables():
    Base.metadata.create_all(bind=engine)