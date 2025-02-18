import qrcode
import base64
from io import BytesIO
from urllib.parse import urlencode


def generate_qr_code(total_cost, transaction_id):
    payee_vpa = "choudharyjitendraz270-1@oksbi"
    payee_name = "Jitendra Choudhary"

    payment_data = {
        "pa": payee_vpa,
        "pn": payee_name,
        "am": str(total_cost),
        "tid": transaction_id,
        "tn": "Payment for print job",
        "cu": "INR",
    }

    upi_url = "upi://pay?" + urlencode(payment_data)
    qr = qrcode.make(upi_url)
    qr.save("test_qr.png")

    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    buffered.seek(0)

    # Convert the buffer to base64
    img_base64 = base64.b64encode(buffered.read()).decode("utf-8")

    return img_base64
