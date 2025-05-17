from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_ENGINE_OPTIONS  # Fixed import

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,  # Using SQLALCHEMY_DATABASE_URI instead of DATABASE_URL
    **SQLALCHEMY_ENGINE_OPTIONS
)

# Create session factory
db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

# Base class for all models
Base = declarative_base()
Base.query = db_session.query_property()

# SQLAlchemy instance for Flask integration
db = SQLAlchemy()

def init_db():
    """Initialize the database and create all tables"""
    # Import models to ensure they're registered with Base
    import models
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

def shutdown_session(exception=None):
    """Remove the session after each request"""
    db_session.remove()