from flask import Blueprint, jsonify, redirect, url_for, current_app
from .auth import signup, login, logout, check_login
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from flask_dance.contrib.google import google
from .models import User
import datetime
import logging
from .db_setup import db

routes = Blueprint('routes', __name__)
logger = logging.getLogger(__name__)

@routes.route('/signup', methods=['POST'])
def signup_route():
    return signup()

@routes.route('/login', methods=['POST'])
def login_route():
    return login()

@routes.route('/logout', methods=['POST'])
@jwt_required()  # Ensure the user is authenticated before logging out
def logout_route():
    return logout()

@routes.route('/check_login', methods=['GET'])
@jwt_required()  # Ensure the user is authenticated before logging out
def check_login_route():
    return check_login()

@routes.route('/protected', methods=['GET'])
@jwt_required()
def protected_route():
    return jsonify({"msg": "This is a protected route"})

@routes.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    response = google.get("/plus/v1/people/me")
    assert response.ok, response.text
    user_info = response.json()
    
    email = user_info["emails"][0]["value"]

    # Check if user exists in DB
    user = User.query.filter_by(email=email).first()
    db_user = user # Assign to a common variable to use after if/else

    if db_user is None:
        # Automatically sign up the user
        logger.info(f"New user signup via Google OAuth: {email}")
        db_user = User(email=email) # Password will be null
        db.session.add(db_user)
        db.session.commit()
    else:
        logger.info(f"User login via Google OAuth: {email}")

    # Generate tokens for the user
    access_token = create_access_token(identity=db_user.email)
    refresh_token = create_refresh_token(identity=db_user.email)

    # Redirect to frontend with tokens
    frontend_url = current_app.config['FRONTEND_URL']
    redirect_url = f"{frontend_url}?access_token={access_token}&refresh_token={refresh_token}"

    logger.info(f"Redirecting Google OAuth user {db_user.email} to frontend.")
    return redirect(redirect_url)

@routes.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_route():
    current_user_identity = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_identity, expires_delta=datetime.timedelta(hours=1))
    logger.info(f"Access token refreshed for user: {current_user_identity}")
    return jsonify(access_token=new_access_token), 200
