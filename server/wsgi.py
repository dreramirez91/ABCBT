from flask import Flask, request, jsonify, make_response, Response
from markupsafe import escape
from pymongo import MongoClient
from dotenv import dotenv_values
from bson import json_util, ObjectId
import json
from json import JSONEncoder
import requests
import pprint
from flask_bcrypt import Bcrypt

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj): return json_util.default(obj)
    
app = Flask(__name__)
bcrypt = Bcrypt(app)

app.json_encoder = CustomJSONEncoder

config = dotenv_values(".env")

with app.app_context():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("\n\n\n", "Connected to MongoDB!", app.database, "\n\n\n")
    
@app.route("/disputations/", methods=['GET', 'POST', 'DELETE'])
def CRUD_all_disputations():
    if request.method == 'GET':
        all_disputations = app.database["disputations"].find()
        data = json.loads(json_util.dumps([d for d in all_disputations]))
        print(type(data), "-------\n\n\n")
        for d in data:
            d["_id"] = d["_id"]["$oid"]
        return {"disputations": data}
    elif request.method == 'POST':
        disputation = request.json
        app.database["disputations"].insert_one(disputation)
        new_disputation = json.loads(json_util.dumps(app.database["disputations"].find_one(
            {"_id": disputation['_id']}))
        )
        return new_disputation
    elif request.method == 'DELETE':
        response = app.database["disputations"].delete_many({})
        print("\n\n\n----------", response, "---------\n\n\n")
        return {"deleted_count": response.deleted_count}

@app.route("/disputations/<id>/", methods=['GET', 'PUT', 'DELETE'])
def CRUD_one_disputation(id):
    if request.method == 'GET':
        one_disputation = app.database["disputations"].find_one({"_id": ObjectId(id)})
        data = json.loads(json_util.dumps(one_disputation))
        return {"disputation": data}
    elif request.method == 'DELETE':
        response = app.database["disputations"].delete_one({"_id": ObjectId(id)})
        print("\n\n\n----------", response, "---------\n\n\n")
        return {"deleted_count": response.deleted_count}
    elif request.method == 'PUT':
        disputation = request.json
        response = app.database["disputations"].replace_one({"_id": ObjectId(id)}, disputation)
        return {"updated_count": response.modified_count}
        
@app.route("/users/", methods=['GET', 'POST', 'DELETE'])
def CRUD_all_users():
    if request.method == 'GET':
        all_users = app.database["users"].find()
        data = json.loads(json_util.dumps([u for u in all_users]))
        for u in data:
            u["_id"] = u["_id"]["$oid"]
        return {"users": data}
    elif request.method == 'POST':
        new_user = request.json
        existing_user = app.database["users"].find_one({"email": new_user["email"]})
        print("\n\n=================\n\n\n\n", existing_user, "\n\n\n\n=================\n\n")
        if existing_user:
            return Response("The email you entered is already tied to an account.", status=400)
        new_user["hashed_password"] = bcrypt.generate_password_hash(new_user["hashed_password"])
        app.database["users"].insert_one(new_user)
        added_user = json.loads(json_util.dumps(app.database["users"].find_one(
             {"_id": new_user['_id']})))
        return added_user
    elif request.method == 'DELETE':
        response = app.database["users"].delete_many({})
        return {"deleted_count": response.deleted_count}
    
    
    
# flake8:noqa
# print("\n\n=================\n\n\n\n", response, "\n\n\n\n=================\n\n")

# SIGN IN
# bcrypt.check_password_hash(users_doc["password"], request.form["password"]) # Just an example of how you could use it.
