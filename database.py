import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. DYNAMIC URL: Get the link and immediately STRIP any hidden spaces
raw_url = os.getenv("DATABASE_URL")

if raw_url:
    # This .strip() removes any accidental spaces at the start or end
    DATABASE_URL = raw_url.strip()
    
    # RENDER FIX: SQLAlchemy 1.4+ requires 'postgresql'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # Fallback for your local machine testing
    DATABASE_URL = "postgresql://postgres:raoinam7462@localhost/mini_bank_db"

# 2. SETUP ENGINE
# Use pool_pre_ping to help maintain the cloud connection
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    Base.metadata.create_all(bind=engine)