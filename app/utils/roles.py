from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.models.users import User


def super_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != "super_admin":
            return jsonify({"message": "Super admin access required"}), 403

        return fn(*args, **kwargs)
    return wrapper