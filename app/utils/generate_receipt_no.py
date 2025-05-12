from flask import current_app
from pymongo import ReturnDocument

def generate_receipt_no():
    """
    Atomically generate a new, zero-padded 6-digit receipt number,
    and update the single document in `receipt_collection` with the new value.
    """
    db = current_app.config.get("DB")
    if db is None:
        raise RuntimeError("Database not initialized in app config")

    # 1) bump the counter in receipt_counters
    counter = db.receipt_counters.find_one_and_update(
        {"_id": "receipt_no"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    seq = counter.get("seq", 0)
    receipt_no = str(seq).zfill(6)  # e.g. "000001"

    # 2) update the single receipt document (create if missing)
    # db.receipt_collection.find_one_and_update(
    #     {"_id": "receipt_no"},
    #     {"$set": {"receipt_no": receipt_no}},
    #     upsert=True
    # )

    return receipt_no
