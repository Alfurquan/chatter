import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load DB connection from environment variables
DB_USER = os.getenv("DB_USER", "chatuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "chatpass")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "chatapp")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function for FastAPI or manual usage
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
