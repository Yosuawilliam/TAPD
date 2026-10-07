import os
import sys

# Set up path so app can be imported properly by Vercel serverless function
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from run import setup_database

app = create_app()

with app.app_context():
    try:
        setup_database(app)
    except Exception as e:
        print(f"Database initialization error on Vercel: {e}")

# Vercel entry point
