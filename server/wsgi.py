from flask import Flask, request
from markupsafe import escape
from pymongo import MongoClient
from dotenv import dotenv_values
from bson import json_util, ObjectId
import json
from json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj): return json_util.default(obj)
    
app = Flask(__name__)

app.json_encoder = CustomJSONEncoder

config = dotenv_values(".env")

with app.app_context():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("\n\n\n", "Connected to MongoDB!", app.database, "\n\n\n")
    
@app.route("/disputations/", methods=['GET', 'POST', 'DELETE'])
def crud_all_disputations():
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
def crud_one_disputation(id):
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
        
    
# flake8:noqa
