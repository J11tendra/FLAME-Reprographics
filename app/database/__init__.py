from flask import current_app
from pymongo import MongoClient
import gridfs
import os


def init_db(app):
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["flame-reprographics"]
    fs = gridfs.GridFS(db)
    app.config["DB"] = db
    app.config["FS"] = fs
