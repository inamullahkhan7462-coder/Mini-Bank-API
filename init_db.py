from database import engine, Base
import models  # This is crucial so SQLAlchemy knows about your tables!

print("Connecting to the database and creating tables...")

# This command actually talks to Postgres and creates the tables
Base.metadata.create_all(bind=engine)

print("Tables created successfully in mini_bank_db!")