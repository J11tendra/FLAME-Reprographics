from flask import (
    Blueprint,
    request,
    render_template,
    current_app,
    jsonify,
    session,
    redirect,
    url_for,
)
import fitz
from app.utils import calculate_cost, generate_qr_code
from bson.objectid import ObjectId

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if session.get("locked"):
        return redirect(url_for("home"))

    if "user" not in session:
        return redirect(url_for("home"))

    db = current_app.config["DB"]
    fs = current_app.config["FS"]

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
            "status": "progress",
        }

        transaction_collection = db.transactions

        if "transaction_id" in session["user"]:
            transaction_id = session["user"]["transaction_id"]
            transaction_collection.update_one(
                {"_id": ObjectId(transaction_id)},
                {"$set": transaction_data},
            )

        else:
            transaction_collection.insert_one(transaction_data)
            session["user"]["transaction_id"] = str(transaction_data["_id"])

            transaction_id = str(
                transaction_data["_id"]
            ) 
        qr_img_io = generate_qr_code(total_cost, transaction_id)

        return render_template(
            "payment.html", total_cost=total_cost, qr_code_img=qr_img_io
        )

    return "No file uploaded", 400
