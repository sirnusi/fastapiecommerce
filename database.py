from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The database file will be created in your project root
SQLALCHEMY_DATABASE_URL = "sqlite:///./ecommerce.db"

# connect_args is needed only for SQLite to allow multiple threads
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each instance of this will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All your database models will inherit from this Base class
Base = declarative_base()
