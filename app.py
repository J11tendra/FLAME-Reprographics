from flask import Flask, session, render_template
import os
from app import create_app

app = create_app()


@app.route("/")
def home():
    user = session.get("user")
    if user:
        return render_template("index.html", user=user)
    return render_template("login.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)