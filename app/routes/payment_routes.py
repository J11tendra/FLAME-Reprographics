from datetime import datetime, date
from flask import (
    Blueprint,
    request,
    render_template,
    current_app,
    session,
    redirect,
    url_for,
)
from app.utils import (
    calculate_cost,
    generate_qr_code,
    verify_payment,
    generate_receipt_no
)
from bson.objectid import ObjectId

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/summary", methods=["GET", "POST"])
def summary():
    db = current_app.config["DB"]
    txn_id = ObjectId(session["user"]["transaction_id"])
    txn = db.transactions.find_one({"_id": txn_id})

    if request.method == "POST":
        utr_id, timestamp = verify_payment(request.files["file"])

        valid = False
        error_msg = None

        if not utr_id:
            error_msg = "UTR ID not found in the uploaded screenshot."
        elif not timestamp:
            error_msg = "Timestamp not found in the uploaded screenshot."
        else:
            try:
                date_formats = ["%d %b %Y", "%d %B %Y", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"]
                txn_date = None
                for fmt in date_formats:
                    try:
                        txn_date = datetime.strptime(timestamp.strip(), fmt).date()
                        break
                    except ValueError:
                        continue

                if not txn_date:
                    error_msg = "Failed to parse the date from timestamp."
                elif txn_date != date.today():
                    error_msg = f"Payment date mismatch. Found: {txn_date.strftime('%d %b %Y')}, expected: {date.today().strftime('%d %b %Y')}."
                else:
                    valid = True
            except Exception:
                error_msg = "Unexpected error while parsing timestamp."

        if not valid:
            num_pages  = txn["numPages"]
            print_type = txn["printType"]
            color      = txn["color"]

            total_cost = calculate_cost(num_pages, print_type, color)
            qr_img     = generate_qr_code(total_cost, str(txn_id))

            return render_template(
                "payment.html",
                total_cost=total_cost,
                qr_code_img=qr_img,
                error=error_msg or "Unverified payment. Please try again."
            )

        update = {"$set": {"utr_id": utr_id, "status": "verified", "timestamp": timestamp}}
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
