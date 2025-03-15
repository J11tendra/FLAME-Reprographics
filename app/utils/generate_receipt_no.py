from flask import current_app

def generate_receipt_no():
    db = current_app.config["DB"]
    receipt_collection = db["receipt_collection"]
    receipt = receipt_collection.find_one({"_id": "receipt_no"})
    
    if receipt is None:
        new_receipt_no = 1
        receipt_collection.insert_one({"_id": "receipt_no", "value": new_receipt_no})
    else:
        new_receipt_no = receipt['value'] + 1
        receipt_collection.update_one({"_id": "receipt_no"}, {"$set": {"value": new_receipt_no}})
    
    return f"{new_receipt_no:06d}"