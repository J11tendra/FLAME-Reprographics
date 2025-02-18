from flask import Flask, redirect, url_for, session, render_template, request
from flask_session import Session
from authlib.integrations.flask_client import OAuth
import json
import os
from dotenv import load_dotenv

# from pymongo import MongoClient
# import gridfs
import fitz
from app.database import init_db

# from app.utils.calculate_cost import calculate_cost
# from app.utils.generate_qr_code import generate_qr_code
# from app.utils.verify_payment_ss import verify_payment

from app.routes import auth_bp, upload_bp, payment_bp, dashboard_bp

# Load environment variables from .env
load_dotenv()

oauth = OAuth()


# Flask app configuration
def create_app():

    # load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    # Flask-Session configuration (stores session in memory)
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # with app.app_context():
    #     init_db()
    # # init_db()

    oauth.init_app(app)
    # MongoDB setup
    # client = MongoClient(os.getenv("MONGODB_URI"))
    # db = client["flame-reprographics"]  # Use the database name from the URI
    # fs = gridfs.GridFS(db)

    # OAuth setup
    # oauth = OAuth(app)
    google = oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        access_token_url="https://oauth2.googleapis.com/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        api_base_url="https://www.googleapis.com/oauth2/v1/",
        userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
        jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
        client_kwargs={
            "scope": "openid email profile https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read"
        },
    )

    # from app.routes import auth_routes, upload_routes, payment_routes
    app.config["google"] = google
    init_db(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(dashboard_bp)

    # Make `app` and `db` accessible
    __all__ = ["app"]

    return app
