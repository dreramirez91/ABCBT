from flask import Flask, request, Response
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import json_util, ObjectId
import json
import os
import pprint
import jwt

from flask_bcrypt import Bcrypt, check_password_hash


app = Flask(__name__)
bcrypt = Bcrypt(app)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

with app.app_context():
    app.mongodb_client = MongoClient(os.getenv("ATLAS_URI"))
    app.database = app.mongodb_client[os.getenv("DB_NAME")]
    print("\n\n=================\n\n\n\n", "Connected to MongoDB!", app.database, "\n\n\n\n=================\n\n")


@app.route("/reframes/", methods=["GET", "POST", "DELETE"])
def CRUD_all_reframes():
    if request.method == "GET":
        all_reframes = app.database["reframes"].find()
        data = json.loads(json_util.dumps([d for d in all_reframes]))
        for r in data:
            r["_id"] = r["_id"]["$oid"]
        return {"reframes": data}
    elif request.method == "POST":
        reframe = request.json
        app.database["reframes"].insert_one(reframe)
        new_reframe = json.loads(
            json_util.dumps(app.database["reframes"].find_one({"_id": reframe["_id"]}))
        )
        return new_reframe
    elif request.method == "DELETE":
        response = app.database["reframes"].delete_many({})
        return {"deleted_count": response.deleted_count}


@app.route("/reframes/<id>/", methods=["GET", "PUT", "DELETE"])
def CRUD_one_reframe(id):
    if request.method == "GET":
        one_reframe = app.database["reframes"].find_one({"_id": ObjectId(id)})
        data = json.loads(json_util.dumps(one_reframe))
        return {"reframe": data}
    elif request.method == "DELETE":
        response = app.database["reframes"].delete_one({"_id": ObjectId(id)})
        return {"deleted_count": response.deleted_count}
    elif request.method == "PUT":
        reframe_data = request.json
        response = app.database["reframes"].replace_one(
            {"_id": ObjectId(id)}, reframe_data
        )
        return {"updated_count": response.modified_count}


@app.route("/users/", methods=["GET", "POST", "DELETE"])
def CRUD_all_users():
    if request.method == "GET":
        all_users = app.database["users"].find()
        data = json.loads(json_util.dumps([u for u in all_users]))
        for u in data:
            u["_id"] = u["_id"]["$oid"]
        return {"users": data}
    elif request.method == "POST":
        new_user = request.json
        existing_user = app.database["users"].find_one({"email": new_user["email"]})
        if existing_user:
            return Response(
                "The email you entered is already tied to an account.", status=400
            )
        new_user["hashed_password"] = bcrypt.generate_password_hash(
            new_user["hashed_password"]
        )
        app.database["users"].insert_one(new_user)
        added_user = json.loads(
            json_util.dumps(app.database["users"].find_one({"_id": new_user["_id"]}))
        )
        return added_user
    elif request.method == "DELETE":
        response = app.database["users"].delete_many({})
        return {"deleted_count": response.deleted_count}

@app.route("/users/login/", methods=["POST"])
def login():
    login_info = request.json
    user_info = app.database["users"].find_one({"email": login_info["email"]})
    user_id = user_info['_id']
    valid_password = check_password_hash(user_info["hashed_password"], login_info["password"])
    if valid_password:
        try:
            token = jwt.encode(
                {"user_id": json_util.dumps(user_id)},
                 app.config["SECRET_KEY"],
                 algorithm="HS256"
            )
            return {
                "message": "Successfully fetched auth token",
                "token": token
            }
        except Exception as e:
            return {
                "message": str(e)
            }, 500
    else:
        return Response(
                "Invalid password.", status=400
            )
         
         
        # give token in response to client using JWT...

# When to prove authorization send token in headers to server
# Authorization: Bearer <token>
# Best place to store tokens are in cookies because they are not accessible via JavaScript like they are in localStorage and sessionStorage
# Cookies are also automatically sent to the server
# Always use HTTPS
# Sessions are stored server-side, tokens stored client-side (therefore more scalable)
# Access-Control-Allow-Origin: *

# flake8:noqa

# print("\n\n=================\n\n\n\n", user_info, "\n\n\n\n=================\n\n")
