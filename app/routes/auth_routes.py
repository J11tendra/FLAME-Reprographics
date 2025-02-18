from flask import Flask, redirect, url_for, session, Blueprint, current_app

from authlib.integrations.flask_client import OAuth
from flask_session import Session
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

# from app import google

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    # from app import google
    google = current_app.config["google"]

    # session["oauth_state"] = os.urandom(24).hex()  /# Ensure state is stored
    return google.authorize_redirect("http://localhost:5000/callback")


@auth_bp.route("/callback")
def callback():
    # from app import db
    db = current_app.config["DB"]

    google = current_app.config["google"]

    try:
        token = google.authorize_access_token()
        user_info = google.get("https://www.googleapis.com/oauth2/v1/userinfo").json()

        # Fetch additional details (age, gender, birthday)
        extra_info = google.get(
            "https://people.googleapis.com/v1/people/me?personFields=birthdays,genders"
        ).json()
        print("Extra info:", extra_info)  # Debugging line

        # Extract gender & birthday safely
        gender = extra_info.get("genders", [{}])[0].get("value", "Not Provided")
        birthday = extra_info.get("birthdays", [{}])[0].get("date", "Not Provided")

        # Store in session
        session["user"] = {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "picture": user_info.get("picture"),
            "gender": gender,
            "birthday": birthday,
        }

        user_data = {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "picture": user_info.get("picture"),
        }

        users_collection = db.users
        users_collection.insert_one(user_data)
        # users_collection.update_one(
        #     {"email": user_info.get("email")}, {"$set": user_data}, upsert=True
        # )

        print("User data:", user_data)  # Debugging line

        return redirect(url_for("home"))

    except Exception as e:
        print("Error:", str(e))
        return "Authentication failed. Check logs for details.", 500


@auth_bp.route("/logout")
def logout():
    # session.pop("user", None)
    try:
        if "transaction_id" in session["user"]:
            transaction_id = session["user"]["transaction_id"]
            db = current_app.config["DB"]
            transaction_collection = db.transactions
            transaction = transaction_collection.find_one(
                {"_id": ObjectId(transaction_id)}
            )
            status = transaction.get("status")
            if status == "progress":
                transaction_collection.delete_one({"_id": ObjectId(transaction_id)})
    except KeyError:
        pass
    session.clear()
    return redirect(url_for("home"))
