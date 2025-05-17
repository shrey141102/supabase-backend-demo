import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Get Supabase connection string from environment variables
raw_database_url = os.environ.get('DATABASE_URL', '')

# Remove pgbouncer parameter from the connection string as psycopg2 doesn't recognize it
# The ?pgbouncer=true parameter is meant for SQLAlchemy behavior, not for the driver
if raw_database_url:
    # Extract the pgbouncer parameter and remove it from the URL
    pgbouncer_enabled = 'pgbouncer=true' in raw_database_url
    database_url = re.sub(r'\?pgbouncer=true', '', raw_database_url)
    # Remove any trailing '&' if it was part of multiple parameters
    database_url = re.sub(r'&pgbouncer=true', '', database_url)
else:
    pgbouncer_enabled = False
    database_url = None

# Export DATABASE_URL for compatibility with existing code
DATABASE_URL = database_url

# For SQLAlchemy, use the cleaned DATABASE_URL
if database_url:
    SQLALCHEMY_DATABASE_URI = database_url
else:
    # Fallback to SQLite for local development if Supabase credentials aren't set
    SQLALCHEMY_DATABASE_URI = os.environ.get('FALLBACK_DATABASE_URL', 'sqlite:///bitespeed.db')

# SQLAlchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
    'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
    'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', 30)),
    'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 1800)),
    'pool_pre_ping': True,  # Verify connections before using
}

# Add special pgbouncer settings if enabled
if pgbouncer_enabled:
    SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {
        # Disable prepared statements as PgBouncer doesn't support them in transaction mode
        'prepared_statement_cache_size': 0,
        'options': '-c statement_timeout=60000'  # 60 second timeout
    }

# App settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
PORT = int(os.environ.get('PORT', 5001))
WORKERS = int(os.environ.get('WORKERS', 4))