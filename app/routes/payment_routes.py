from flask import (
    flash,
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
from app.utils import generate_receipt_no, calculate_cost, generate_qr_code
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
    transaction_collection = db.transactions
    transaction = transaction_collection.find_one({"_id": ObjectId(transaction_id)})
    utr_id, is_valid = verify_payment(payment_ss, expected_amount=transaction.get("totalCost", 0))
    if not is_valid:
        transaction_id = session["user"]["transaction_id"]
        total_cost = transaction.get("totalCost")
        flash("Payment verification failed. Please upload a valid payment screenshot.", "error")
        # transaction_id = str(
        #         transaction_data["_id"]
        #     )  # Use the MongoDB transaction ID as the unique transaction ID
        qr_img_io = generate_qr_code(total_cost, transaction_id)
        return render_template( "payment.html", total_cost=total_cost, qr_code_img=qr_img_io)

    if utr_id:
        additional_data = {"utr_id": utr_id, "status":"verified"}
    else:
        additional_data = {"utr_id": utr_id, "status": "unsuccessful"}

    update_query = {"_id": ObjectId(transaction_id)}
    update_data = {"$set": additional_data}
    transaction_collection.find_one_and_update(
        update_query, update_data, return_document=True
    )
    
    receipt_no = None
    
    if transaction:
        receipt_no = transaction.get("receipt_no")

        # If receipt_no is missing, generate it and update the database
        if receipt_no is None:
            receipt_no = generate_receipt_no()
            transaction_collection.update_one({"_id": ObjectId(transaction_id)}, {"$set": {"receipt_no": receipt_no}})

            # Fetch transaction again to get the new receipt_no
            transaction = transaction_collection.find_one({"_id": ObjectId(transaction_id)})
            receipt_no = transaction.get("receipt_no")

    
    return render_template("summary.html", receipt_no=receipt_no if receipt_no else "N/A")
