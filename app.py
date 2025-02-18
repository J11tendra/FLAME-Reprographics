from flask import Flask, session, render_template
from app import create_app

app = create_app()


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


if __name__ == "__main__":
    app.run(debug=True)
