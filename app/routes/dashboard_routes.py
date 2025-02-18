from flask import (
    Blueprint,
    request,
    render_template,
    current_app,
    session,
    redirect,
    url_for,
    jsonify,
    Response,
)
import time
from bson.objectid import ObjectId
from bson.json_util import dumps

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))

    db = current_app.config["DB"]
    transaction_collection = db.transactions
    completed_transactions = transaction_collection.find({"status": "completed"})
    transaction_list = list(completed_transactions)

    return render_template("dashboard.html", transactions=transaction_list)


@dashboard_bp.route("/polling")
def polling():
    if "user" not in session:
        return redirect(url_for("home"))

    try:
        db = current_app.config["DB"]
        transaction_collection = db.transactions
        completed_transactions = transaction_collection.find({"status": "completed"})
        transaction_list = list(completed_transactions)

        # Serialize the data properly before sending as JSON
        transaction_list_json = dumps(transaction_list)

        return jsonify({"transactions": transaction_list_json})

    except Exception as e:
        current_app.logger.error(f"Error fetching polling data: {e}")
        return jsonify({"error": "An error occurred while fetching data."}), 500
