from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os

# --- Database Configuration ---
class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = '.env'
        extra = 'ignore'  # Allow extra environment variables

settings = Settings()

# SQLAlchemy engine
# Handle different database types (SQLite vs PostgreSQL)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}  # Required for SQLite

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

# Database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# --- Dependency for getting a DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
