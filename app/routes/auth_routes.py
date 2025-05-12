from flask import Flask, redirect, url_for, session, Blueprint, current_app, request
from authlib.integrations.flask_client import OAuth
from flask_session import Session
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    google = current_app.config["google"]
    redirect_uri = url_for("auth.callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route("/callback")
def callback():
    db = current_app.config.get("DB")
    google = current_app.config["google"]

    try:
        token = google.authorize_access_token()

        resp = google.get("userinfo")
        resp.raise_for_status()
        user_info = resp.json()

        session["user"] = {
            "name":  user_info["name"],
            "email": user_info["email"]
        }

        users_collection = db.users
        users_collection.insert_one({
            "name":  user_info["name"],
            "email": user_info["email"]
        })

        return redirect(url_for("home"))

    except Exception as e:
        logging.exception("OAuth callback failed")
        return f"Authentication failed: {e}", 500

@auth_bp.route("/logout")
def logout():
    try:
        if "transaction_id" in session.get("user", {}):
            transaction_id = session["user"]["transaction_id"]
            db = current_app.config["DB"]
            transaction_collection = db.transactions
            transaction = transaction_collection.find_one(
                {"_id": ObjectId(transaction_id)}
            )
            if transaction and transaction.get("status") == "progress":
                transaction_collection.delete_one({"_id": ObjectId(transaction_id)})
    except KeyError:
        pass
    session.clear()
    return redirect(url_for("home"))
