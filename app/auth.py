from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, JWTManager
from .models import User, TokenBlacklist
from .db_setup import db
import datetime
import logging

logger = logging.getLogger(__name__)
jwt = JWTManager()

def signup():
    email = request.json.get('email')
    password = request.json.get('password')

    if User.query.filter_by(email=email).first():
        logger.warning(f"Signup attempt with existing email: {email}")
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    logger.info(f"User created successfully: {email}")
    return jsonify({"msg": "User created successfully"}), 201

def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        logger.warning(f"Login attempt for non-existent user: {email}")
        return jsonify({"msg": "Bad email or password"}), 401

    if not user.check_password(password):
        logger.warning(f"Invalid password attempt for user: {email}")
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=email, expires_delta=datetime.timedelta(hours=1))
    refresh_token = create_refresh_token(identity=email)
    logger.info(f"User logged in successfully: {email}")
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@jwt_required()
def check_login():
    return jsonify({"msg": "You are logged in!"}), 200

@jwt_required()
def logout():
    jti = get_jwt()['jti']
    token = TokenBlacklist(jti=jti)
    db.session.add(token)
    db.session.commit()
    logger.info(f"User logged out successfully. Token JTI blacklisted: {jti}")
    return jsonify({"msg": "Successfully logged out"}), 200

# Create a custom JWT loader that checks for blacklisted tokens
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token = TokenBlacklist.query.filter_by(jti=jti).one_or_none()
    return token is not None