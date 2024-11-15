from flask import Flask
#from flask_jwt_extended import JWTManager
from .routes import routes
from .db_setup import init_db
from dotenv import load_dotenv
import os
from .auth import jwt
from flask_dance.contrib.google import make_google_blueprint, google

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') 
    app.debug = True
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