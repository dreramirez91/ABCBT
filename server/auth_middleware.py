from functools import wraps
import jwt
from flask import request, current_app
import json
from bson import ObjectId


def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
        if not token:
            return {
                "error": "Unauthorized",
                "message": "Authentication token is missing.",
            }, 401
        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            json_user_dict = data["user_id"]
            python_user_dict = json.loads(json_user_dict)
            user_id = python_user_dict["$oid"]
            current_user = current_app.database["users"].find_one(
                {"_id": ObjectId(user_id)}
            )
            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized",
                }, 401
        except Exception as e:
            return {"error": str(e)}, 500
        return function(*args, **kwargs)

    return decorated
