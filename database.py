from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual Postgres credentials
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:raoinam7462@localhost/mini_bank_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This function will create the tables in Postgres
def create_tables():
    Base.metadata.create_all(bind=engine)