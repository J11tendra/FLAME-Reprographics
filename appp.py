from flask import Flask, redirect, url_for, session, render_template, request
from flask_session import Session
from authlib.integrations.flask_client import OAuth
import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import gridfs
import fitz
from utils import calculate_cost, generate_qr_code, verify_payment

# Load environment variables from .env
load_dotenv()

# Flask app configuration
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Flask-Session configuration (stores session in memory)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["flame-reprographics"]  # Use the database name from the URI
fs = gridfs.GridFS(db)

# OAuth setup
oauth = OAuth(app)
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


@app.route("/")
def home():
    user = session.get("user")
    if user:
        return render_template("index.html", user=user)

    # return f"""
    # <h1>Welcome, {user.get('name', 'Unknown')}</h1>
    # <p>Email: {user.get('email', 'Unknown')}</p>
    # <p>Gender: {user.get('gender', 'Not Provided')}</p>
    # <p>Birthday: {user.get('birthday', 'Not Provided')}</p>
    # <img src="{user.get('picture', '')}" width="100" height="100">
    # <br><a href="/logout">Logout</a>
    # """
    return render_template("login.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    print_type = request.form["printType"]
    color = request.form["color"]

    if file:
        pdf_data = file.read()
        pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
        num_pages = len(pdf_doc)
        file_id = fs.put(file, filename=file.filename, content_type=file.content_type)

        total_cost = calculate_cost(num_pages, print_type, color)

        transaction_data = {
            "file_id": file_id,
            "filename": file.filename,
            "printType": print_type,
            "color": color,
            "numPages": num_pages,
            "totalCost": total_cost,
        }

        db.transactions.insert_one(transaction_data)

        # Generate the QR code
        transaction_id = str(
            transaction_data["_id"]
        )  # Use the MongoDB transaction ID as the unique transaction ID
        qr_img_io = generate_qr_code(total_cost, transaction_id)

        return render_template(
            "payment.html", total_cost=total_cost, qr_code_img=qr_img_io
        )

    return "No file uploaded", 400


@app.route("/login")
def login():
    # session["oauth_state"] = os.urandom(24).hex()  /# Ensure state is stored
    return google.authorize_redirect("http://localhost:5000/callback")


@app.route("/callback")
def callback():
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


@app.route("/summary", methods=["POST"])
def summary():
    payment_ss = request.files["file"]
    print("screenshot:" + payment_ss.filename)
    utr_id = verify_payment(payment_ss)
    transaction_collection = db.transactions
    transaction_collection.insert_one({"utr_id": utr_id})
    return render_template("summary.html")


@app.route("/logout")
def logout():
    # session.pop("user", None)
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
