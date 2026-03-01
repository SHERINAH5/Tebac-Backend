from flask import Blueprint, request, jsonify, current_app
from app.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
)
import validators
from app.models.users import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, bcrypt



users = Blueprint("users", __name__, url_prefix="/api/v1/users")


# 🔐 Super Admin: Get All Users
@users.route("/", methods=["GET"])
@jwt_required()
def get_all_users():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != "super_admin":
        return jsonify({"error": "Access denied"}), HTTP_403_FORBIDDEN

    all_users = User.query.all()
    result = [{
        "id": u.id,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "biography": u.biography,
        "contact": u.contact,
        "role": u.role,
    } for u in all_users]

    return jsonify(result), HTTP_200_OK

# Get user by ID (Admin, Super Admin, or self)
@users.route("/user/<int:id>", methods=["GET"])
@jwt_required()
def get_user_by_id(id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    target_user = User.query.get(id)

    if not target_user:
        return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

    # Super Admin or Admin can view any user, others only themselves
    if current_user.role not in ["super_admin", "admin"] and current_user.id != id:
        return jsonify({"error": "Access denied"}), HTTP_403_FORBIDDEN

    return jsonify({
        "id": target_user.id,
        "first_name": target_user.first_name,
        "last_name": target_user.last_name,
        "email": target_user.email,
        "contact": target_user.contact,
        "biography": target_user.biography,
        "role": target_user.role,
        "created_at": target_user.created_at,
        "updated_at": target_user.updated_at,
    }), HTTP_200_OK

# 🔄 Update user (self or super_admin)
@users.route("/edit/<int:id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_user_details(id):
    try:
        payload = request.get_json(silent=True) or {}
        current_user = User.query.get(get_jwt_identity())
        user = User.query.get(id)

        if not user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        # Authorization: super_admin or self
        if current_user.id != user.id and current_user.role != "super_admin":
            return jsonify({"error": "Access denied"}), HTTP_403_FORBIDDEN

        # Update fields (self can only update basic info)
        restricted_fields = ["role", "email"]
        for field in restricted_fields:
            if current_user.role != "super_admin":
                payload.pop(field, None)

        if "email" in payload:
            email = payload["email"].strip().lower()
            if not validators.email(email):
                return jsonify({"error": "Invalid email format"}), HTTP_400_BAD_REQUEST
            if User.query.filter(User.email == email, User.id != user.id).first():
                return jsonify({"error": "Email already in use"}), HTTP_409_CONFLICT
            user.email = email

        if "contact" in payload and payload["contact"] != user.contact:
            if User.query.filter(User.contact == payload["contact"], User.id != user.id).first():
                return jsonify({"error": "Contact already in use"}), HTTP_409_CONFLICT
            user.contact = payload["contact"]

        for field in ["first_name", "last_name", "biography", "role"]:
            if field in payload:
                setattr(user, field, payload[field])

        if "password" in payload and payload["password"]:
            user.password = bcrypt.generate_password_hash(payload["password"]).decode("utf-8")

        db.session.commit()

        return jsonify({
            "message": f"{user.get_full_name()}'s details have been updated.",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "contact": user.contact,
                "role": user.role,
                "biography": user.biography,
                "updated_at": user.updated_at,
            }
        }), HTTP_200_OK

    except Exception as e:
        current_app.logger.exception("Failed to update user.")
        return jsonify({"error": "Failed to update user."}), HTTP_500_INTERNAL_SERVER_ERROR


#  Super Admin: Delete a user
@users.route("/delete/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != "super_admin":
        return jsonify({"error": "Access denied"}), HTTP_403_FORBIDDEN

    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully."}), HTTP_200_OK
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete user."}), HTTP_500_INTERNAL_SERVER_ERROR