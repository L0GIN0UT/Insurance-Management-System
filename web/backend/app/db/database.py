from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from typing import Generator

# Database URL from environment variables
MAIN_DB_NAME = os.getenv("MAIN_DB_NAME", "main_db")
MAIN_DB_USER = os.getenv("MAIN_DB_USER", "main_user")
MAIN_DB_PASSWORD = os.getenv("MAIN_DB_PASSWORD", "main_pass")
MAIN_DB_HOST = os.getenv("MAIN_DB_HOST", "localhost")
MAIN_DB_PORT = os.getenv("MAIN_DB_PORT", "5432")

DATABASE_URL = f"postgresql://{MAIN_DB_USER}:{MAIN_DB_PASSWORD}@{MAIN_DB_HOST}:{MAIN_DB_PORT}/{MAIN_DB_NAME}"

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True
)

# Session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for declarative models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all tables defined in models
    """
    Base.metadata.create_all(bind=engine) 