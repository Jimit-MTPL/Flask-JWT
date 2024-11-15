from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, JWTManager
from .models import User
from .db_setup import db
import datetime


blacklist = set()
jwt = JWTManager()

def signup():
    email = request.json.get('email')
    password = request.json.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad credentials"}), 401

    access_token = create_access_token(identity=email, expires_delta=datetime.timedelta(hours=1))
    return jsonify(access_token=access_token), 200

@jwt_required()
def check_login():
    return jsonify({"msg": "You are logged in!"}), 200

@jwt_required()
def logout():
    # Add the token to the blacklist
    jti = get_jwt()['jti']  # Get the unique identifier for the JWT
    blacklist.add(jti)  # Add the token to the blacklist
    return jsonify({"msg": "Successfully logged out"}), 200

# Create a custom JWT loader that checks for blacklisted tokens
"""
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blacklist
"""