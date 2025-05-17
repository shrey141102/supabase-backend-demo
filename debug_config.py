
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print environment variables
print("Environment variables:")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"DEBUG: {os.environ.get('DEBUG')}")
print(f"PORT: {os.environ.get('PORT')}")

# Try importing the config module
print("\nImporting config module...")
try:
    import config
    print("Config module imported successfully!")
    
    # Print config variables
    print("\nConfig variables:")
    print(f"SQLALCHEMY_DATABASE_URI: {getattr(config, 'SQLALCHEMY_DATABASE_URI', 'Not found')}")
    print(f"DATABASE_URL: {getattr(config, 'DATABASE_URL', 'Not found')}")
    
    # Try importing database module
    print("\nImporting database module...")
    try:
        import database
        print("Database module imported successfully!")
    except ImportError as e:
        print(f"Failed to import database module: {e}")
        
except ImportError as e:
    print(f"Failed to import config module: {e}")

print("\nScript completed")