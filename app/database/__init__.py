from flask import current_app
from pymongo import MongoClient
import gridfs
import os


def init_db(app):
    # with app.app_context():
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["flame-reprographics"]  # Use the database name from the URI
    fs = gridfs.GridFS(db)
    app.config["DB"] = db
    app.config["FS"] = fs
