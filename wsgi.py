from app import create_app

# Create the application instance
application = create_app()
app = application  # For compatibility with both Gunicorn and other WSGI servers

if __name__ == "__main__":
    application.run()