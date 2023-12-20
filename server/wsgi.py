from flask import Flask, request, Response
from pymongo import MongoClient
from dotenv import dotenv_values
from bson import json_util, ObjectId
import json
import pprint
from flask_bcrypt import Bcrypt


app = Flask(__name__)
bcrypt = Bcrypt(app)

config = dotenv_values(".env")

with app.app_context():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("\n\n\n", "Connected to MongoDB!", app.database, "\n\n\n")


@app.route("/reframes/", methods=["GET", "POST", "DELETE"])
def CRUD_all_reframes():
    if request.method == "GET":
        all_reframes = app.database["reframes"].find()
        data = json.loads(json_util.dumps([d for d in all_reframes]))
        print(type(data), "-------\n\n\n")
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
        print("\n\n\n----------", response, "---------\n\n\n")
        return {"deleted_count": response.deleted_count}


@app.route("/reframes/<id>/", methods=["GET", "PUT", "DELETE"])
def CRUD_one_reframe(id):
    if request.method == "GET":
        one_reframe = app.database["reframes"].find_one({"_id": ObjectId(id)})
        data = json.loads(json_util.dumps(one_reframe))
        return {"reframe": data}
    elif request.method == "DELETE":
        response = app.database["reframes"].delete_one({"_id": ObjectId(id)})
        print("\n\n\n----------", response, "---------\n\n\n")
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


# flake8:noqa
# print("\n\n=================\n\n\n\n", response, "\n\n\n\n=================\n\n")

# SIGN IN
# bcrypt.check_password_hash(users_doc["password"], request.form["password"]) # Just an example of how you could use it.
