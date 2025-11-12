"""Main Flask application entry point."""
import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app()

if __name__ == '__main__':
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    app.run(host=host, port=port, debug=debug)
