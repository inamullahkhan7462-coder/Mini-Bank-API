from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual Postgres credentials
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:raoinam7462@localhost/mini_bank_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import os

# 1. Try to get the link from Render's environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. If it's NOT on Render (like when you are working on your laptop), use your local link
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:your_local_password@localhost/minibank"

# 3. Fix for Render/SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 4. Create the engine using the dynamic URL
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# This function will create the tables in Postgres
def create_tables():
    Base.metadata.create_all(bind=engine)

