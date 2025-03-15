from flask import Flask, redirect, url_for, session, Blueprint, current_app, request

from authlib.integrations.flask_client import OAuth
from flask_session import Session
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    google = current_app.config["google"]
    return google.authorize_redirect("http://localhost:5000/callback")


@auth_bp.route("/callback")
def callback():
    # from app import db
    db = current_app.config["DB"]

    google = current_app.config["google"]

    try:
        token = google.authorize_access_token()
        user_info = google.get("https://www.googleapis.com/oauth2/v1/userinfo").json()

        # Store in session
        session["user"] = {
            "name": user_info.get("name"),
            "email": user_info.get("email")
        }

        user_data = {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
        }

        # users_collection = db.users
        # users_collection.insert_one(user_data)
        transaction_collection = db.transactions
        transaction_collection.insert_one(user_data)
        session["user"]["transaction_id"] = str(user_data["_id"])
        return redirect(url_for("home"))

    except Exception as e:
        print(str(e))
        return "Authentication failed. Check logs for details.", 500


# @auth_bp.route("/logout")
# def logout():
#     try:
#         if "transaction_id" in session["user"]:
#             transaction_id = session["user"]["transaction_id"]
#             db = current_app.config["DB"]
#             transaction_collection = db.transactions
#             transaction = transaction_collection.find_one(
#                 {"_id": ObjectId(transaction_id)}
#             )
#             status = transaction.get("status")
#             if status == "progress":
#                 transaction_collection.delete_one({"_id": ObjectId(transaction_id)})
#     except KeyError:
#         session.clear()
#     return redirect(url_for("home"))

@auth_bp.route("/logout")
def logout():
    try:
        if "user" in session and "transaction_id" in session["user"]:
            transaction_id = session["user"]["transaction_id"]
            db = current_app.config["DB"]
            transaction_collection = db.transactions
            
            transaction = transaction_collection.find_one({"_id": ObjectId(transaction_id)})

            if transaction:
                status = transaction.get("status", "")
                if not status or status == "pending":
                    transaction_collection.delete_one({"_id": ObjectId(transaction_id)})
            
        session.clear()
    
    except Exception as e:
        current_app.logger.error(f"Error during logout: {e}")
    
    return redirect(url_for("home"))
