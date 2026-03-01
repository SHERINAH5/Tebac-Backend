from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.status_codes import HTTP_200_OK, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_202_ACCEPTED,HTTP_401_UNAUTHORIZED,HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from datetime import timedelta
from app.extensions import db
from app.models.users import User

auth = Blueprint("auth", __name__)



# Register
@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required_fields = ["name", "email", "password", "contact", "biography"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"{field} is required"}), HTTP_400_BAD_REQUEST

    # Check if user exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), HTTP_409_CONFLICT

    if User.query.filter_by(contact=data["contact"]).first():
        return jsonify({"message": "Contact already registered"}), HTTP_409_CONFLICT

    # 🔥 FIRST USER = SUPER ADMIN
    is_first_user = User.query.count() == 0
    assigned_role = "super_admin" if is_first_user else "user"

    user = User(
        name=data["name"],
        email=data["email"],
        contact=data["contact"],
        biography=data["biography"],
        address=data.get("address"),
        gender=data.get("gender"),
        image=data.get("image"),
        role=assigned_role,
    )

    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "role_assigned": assigned_role,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), HTTP_201_CREATED
# Login

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if "email" not in data or "password" not in data:
        return jsonify({"message": "Email and password are required"}), HTTP_400_BAD_REQUEST

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "Invalid credentials"}), HTTP_401_UNAUTHORIZED

    access_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(days=7)
    )

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), HTTP_200_OK



# Get current user 

@auth.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), HTTP_404_NOT_FOUND

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "contact": user.contact,
        "role": user.role
    }), HTTP_200_OK



# Forgot Password 

@auth.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()

    if "email" not in data:
        return jsonify({"message": "Email is required"}),HTTP_400_BAD_REQUEST

    user = User.query.filter_by(email=data["email"]).first()

    # Always return same message (security)
    if not user:
        return jsonify({
            "message": "If the email exists, a reset link will be sent"
        }), HTTP_200_OK

    reset_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(minutes=15)
    )

    # TODO: send reset_token via email (Brevo)
    # For now, we return it for testing
    return jsonify({
        "message": "Password reset token generated",
        "reset_token": reset_token
    }), HTTP_200_OK