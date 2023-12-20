from flask import Flask, request
from markupsafe import escape
from pymongo import MongoClient
from dotenv import dotenv_values
from bson import json_util
import json
import pprint
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
async def add_disputation():
    if request.method == 'GET':
        all_disputations = app.database["disputations"].find()
        data = json.loads(json_util.dumps([d for d in all_disputations]))
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
        return {"response": response.deleted_count}

# flake8:noqa
