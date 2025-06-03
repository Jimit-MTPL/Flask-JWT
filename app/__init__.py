from flask import Flask
#from flask_jwt_extended import JWTManager
from .routes import routes
from .db_setup import init_db # db instance is created here
from dotenv import load_dotenv
import os
import datetime
import logging
from .auth import jwt
from . import models # Import models to make them known to SQLAlchemy for db.create_all()
from flask_dance.contrib.google import make_google_blueprint, google
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app) # Enable CORS for all routes and origins by default

    # Basic Logging Configuration
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'a-default-flask-secret-key') # General Flask secret key
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-default-secret-key-for-dev')  # Strong key in prod env var
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=30)
    app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', '/frontend/web-client/oauth_callback.html') # Changed default

    app.debug = True # TODO: Set to False in production
    jwt.init_app(app)

    # Initialize database
    db = init_db(app) # db object is initialized by init_db

    # Comment out automatic db.create_all() to prefer manual CLI command
    # with app.app_context():
    #     db.create_all()

    # Define CLI command for database initialization
    @app.cli.command("init-db")
    def init_db_command():
        """Creates the database tables."""
        # Need to ensure models are imported somewhere before db.create_all() is called.
        # models are imported at the top of this file now.
        with app.app_context(): # Ensure commands run within app context
            db.create_all()
        print("Initialized the database.")

    google_bp = make_google_blueprint(
        client_id=os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
        redirect_to="routes.google_login"
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    # Register routes
    app.register_blueprint(routes)

    return app