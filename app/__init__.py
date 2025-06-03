from flask import Flask
#from flask_jwt_extended import JWTManager
from .routes import routes
from .db_setup import init_db
from dotenv import load_dotenv
import os
import datetime
import logging
from .auth import jwt
from flask_dance.contrib.google import make_google_blueprint, google

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Basic Logging Configuration
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'a-default-flask-secret-key') # General Flask secret key
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-default-secret-key-for-dev')  # Strong key in prod env var
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=30)

    app.debug = True # TODO: Set to False in production
    jwt.init_app(app)

    # Initialize database
    db = init_db(app)
    with app.app_context():
        db.create_all()

    google_bp = make_google_blueprint(
        client_id=os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
        redirect_to="routes.google_login"
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    # Register routes
    app.register_blueprint(routes)

    return app