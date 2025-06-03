from flask import Blueprint, jsonify, redirect, url_for
from .auth import signup, login, logout, check_login
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
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

    if user is None:
        # Automatically sign up the user
        new_user = User(email=email)
        db.session.add(new_user)
        db.session.commit()

    # Return success or token
    return jsonify({"msg": "Logged in with Google"}), 200

@routes.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_route():
    current_user_identity = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_identity, expires_delta=datetime.timedelta(hours=1))
    logger.info(f"Access token refreshed for user: {current_user_identity}")
    return jsonify(access_token=new_access_token), 200
