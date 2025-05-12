from flask import (
    Blueprint,
    request,
    render_template,
    current_app,
    session,
    redirect,
    url_for,
)
from app.utils import calculate_cost, generate_qr_code, verify_payment, generate_receipt_no
from bson.objectid import ObjectId

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/summary", methods=["GET", "POST"])
def summary():
    db = current_app.config["DB"]
    txn_id = ObjectId(session["user"]["transaction_id"])
    txn = db.transactions.find_one({"_id": txn_id})

    if request.method == "POST":
        utr_id = verify_payment(request.files["file"])

        if not utr_id:
            num_pages  = txn["numPages"]
            print_type = txn["printType"]
            color      = txn["color"]

            total_cost = calculate_cost(num_pages, print_type, color)
            qr_img     = generate_qr_code(total_cost, str(txn_id))

            return render_template(
                "payment.html",
                total_cost=total_cost,
                qr_code_img=qr_img,
                error="unverified"
            )

        update = {"$set": {"utr_id": utr_id, "status": "verified"}}
        if not txn.get("receipt_no"):
            new_no = generate_receipt_no()
            update["$set"]["receipt_no"] = new_no
            receipt_no = new_no
        else:
            receipt_no = txn["receipt_no"]

        db.transactions.find_one_and_update({"_id": txn_id}, update)
        return redirect(url_for("payment.summary", receipt_no=receipt_no))

    receipt_no = request.args.get("receipt_no")
    return render_template("summary.html", receipt_no=receipt_no)
