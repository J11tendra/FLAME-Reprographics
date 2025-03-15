from flask import (
    Blueprint,
    request,
    render_template,
    current_app,
    session,
    jsonify,
    redirect,
    url_for,
)
from app.utils.verify_payment_ss import verify_payment
from app.utils import generate_receipt_no
from bson.objectid import ObjectId

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/summary", methods=["POST"])
def summary():
    if "user" not in session or "transaction_id" not in session["user"]:
        return redirect(url_for("home"))

    session["locked"] = True

    transaction_id = session["user"]["transaction_id"]

    db = current_app.config["DB"]

    payment_ss = request.files["file"]
    utr_id = verify_payment(payment_ss)
    transaction_collection = db.transactions
    if utr_id:
        additional_data = {"utr_id": utr_id, "status":"verified"}
    else:
        additional_data = {"utr_id": utr_id, "status": "unsuccessful"}

    update_query = {"_id": ObjectId(transaction_id)}
    update_data = {"$set": additional_data}
    transaction_collection.find_one_and_update(
        update_query, update_data, return_document=True
    )
    
    receipt_no = generate_receipt_no()
    return render_template("summary.html", receipt_no=receipt_no)
