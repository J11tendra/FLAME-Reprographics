# import os
# import cv2
# import pytesseract
# import re
# import numpy as np
# import numpy as np
# import cv2
# import pytesseract
# import re
# from datetime import datetime, timedelta


# def verify_payment(image_file, expected_amount):
#     try:
#         # Convert uploaded image to NumPy array
#         file_bytes = np.frombuffer(image_file.read(), np.uint8)
#         image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

#         if image is None:
#             raise ValueError("Error: Could not load the image.")

#         # Convert to grayscale
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#         # Apply adaptive thresholding for better OCR accuracy
#         gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#         # Perform OCR
#         extracted_text = pytesseract.image_to_string(gray)

#         print(f"\nExtracted Text:\n{extracted_text}\n")

#         utr_patterns = [
#             r"\b\d{12}\b",  # 12-digit UTRs
#             r"\b[A-Z0-9]{16,22}\b",  # Some UTRs contain letters & are longer
#         ]

#         # Search for UTR ID
#         # for pattern in utr_patterns:
#         #     match = re.search(pattern, extracted_text)
#         #     if match:
#         #         return match.group()  # Return the first UTR found

#         # return ""
    
#          # Extract UTR
#         utr_id = None
#         for pattern in utr_patterns:
#             match = re.search(pattern, extracted_text)
#             if match:
#                 utr_id = match.group()
#                 break  # Stop at the first match

#         if not utr_id:
#             return "No valid UTR found"

#         # **Check for the "To" field**
#         if "flame university" not in extracted_text.lower():
#             return "Invalid recipient"

#         time_patterns = [
#             r"(\d{2}:\d{2}(?:\s?[APap][Mm])?)",  # Matches "14:30" or "2:30 PM"
#             r"(\d{2}-\d{2}-\d{4}\s\d{2}:\d{2})"  # Matches "DD-MM-YYYY HH:MM"
#         ]

#         now = datetime.now()
#         valid_time = False
#         extracted_times = []

#         for pattern in time_patterns:
#             matches = re.findall(pattern, extracted_text)
#             extracted_times.extend(matches)

#         for extracted_time_str in extracted_times:
#             try:
#                 # Convert to datetime object
#                 if ":" in extracted_time_str:
#                     extracted_time = datetime.strptime(extracted_time_str, "%H:%M")
#                 else:
#                     extracted_time = datetime.strptime(extracted_time_str, "%d-%m-%Y %H:%M")

#                 # Calculate time difference
#                 time_diff = now - extracted_time
#                 if timedelta(minutes=-5) <= time_diff <= timedelta(minutes=5):
#                     valid_time = True
#                     break
#             except ValueError:
#                 continue  # Skip invalid time formats

#         if not valid_time:
#             print(extracted_times)
#             print("Transaction time out of valid window")

#         # **Extract & Print All Amounts**
#         amount_pattern = r"₹?\s?([\d,]+\.\d{2})"  # Matches ₹1234.56 or 1234.56
#         amount_matches = re.findall(amount_pattern, extracted_text)

#         # Remove commas and convert to float
#         extracted_amounts = [float(amount.replace(",", "")) for amount in amount_matches]

#         print(f"💰 Extracted Amounts: {extracted_amounts}")

#         if not extracted_amounts:
#             return "Amount not found"

#         # Compare extracted amounts with expected amount
#         if not any(abs(amount - expected_amount) <= 0.01 for amount in extracted_amounts):
#             return f"Incorrect amount: Expected {expected_amount}, Found {extracted_amounts}"

#         # ✅ If all checks pass, return UTR ID
#         return utr_id

#     except Exception as e:
#         print(f"Error processing payment image: {e}")
#         return "Error in processing"



















import cv2
import pytesseract
import re
import numpy as np
from datetime import datetime, timedelta

def preprocess_image(image):
    """Preprocess image for better OCR accuracy."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]  # Thresholding
    kernel = np.ones((1, 1), np.uint8)
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)  # Denoising
    return gray

def extract_utr(text):
    """Extract UTR ID from the text."""
    utr_patterns = [
        r"\b\d{12}\b",  # 12-digit UTRs
        r"\b[A-Z0-9]{16,22}\b",  # UTRs with letters & numbers
    ]
    for pattern in utr_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    return None

def extract_time(text):
    """Extract and validate the transaction time."""
    time_patterns = [
        r"(\d{1,2}:\d{2}\s?[APap][Mm])",  # Matches "10:25 PM" format
    ]
    
    now = datetime.now()
    extracted_times = []

    for pattern in time_patterns:
        matches = re.findall(pattern, text)
        extracted_times.extend(matches)

    for extracted_time_str in extracted_times:
        try:
            extracted_time = datetime.strptime(extracted_time_str, "%I:%M %p")  # Convert to datetime object
            extracted_time = extracted_time.replace(year=now.year, month=now.month, day=now.day)  # Adjust date
            
            # Check if within a 5-minute window
            if timedelta(minutes=-15) <= now - extracted_time <= timedelta(minutes=15):
                return extracted_time_str, True
        except ValueError:
            continue  # Ignore invalid time formats

    return extracted_times if extracted_times else None, False  # Return all extracted times for debugging

# def extract_amount(text, expected_amount):
#     """Extract and validate the amount from the text."""
#     amount_pattern = r"₹?\s?([\d,]+\.\d{2})"
#     amount_matches = re.findall(amount_pattern, text)

#     extracted_amounts = [float(amount.replace(",", "")) for amount in amount_matches]  # Convert to float

#     for amount in extracted_amounts:
#         if abs(amount - expected_amount) <= 0.01:
#             return amount, True

#     return extracted_amounts if extracted_amounts else None, False  # Return all extracted amounts for debugging

def extract_amount(text, expected_amount):
    """Extract and validate the amount from the text, including whole numbers."""
    
    # Updated regex to match both decimal and whole numbers
    amount_pattern = r"₹?\s?([\d,]+(?:\.\d{2})?)"
    
    amount_matches = re.findall(amount_pattern, text)
    
    # Convert extracted amounts to float (handle cases without decimals)
    # extracted_amounts = [float(amount.replace(",", "")) for amount in amount_matches]
    extracted_amounts = []
    for amount in amount_matches:
        try:
            cleaned_amount = amount.replace(",", "")  # Remove commas safely
            extracted_amounts.append(float(cleaned_amount))  # Convert to float
        except ValueError:
            print(f"Skipping invalid amount: {amount}")  # Debugging log

    for amount in extracted_amounts:
        extract_amount_str = str(expected_amount)
        if abs(amount - expected_amount) <= 0.01:
            return amount, True
        
        amount_str = str(int(amount))  # Convert float to string after removing decimals
        if amount_str[-len(extract_amount_str):] == extract_amount_str:
            print(amount_str[-len(extract_amount_str):])
            return amount_str[-len(extract_amount_str):], True
        # elif amount[-len(extract_amount_str):] == expected_amount:
        #     return amount[-len(extract_amount_str):], True

    return extracted_amounts if extracted_amounts else None, False 

def verify_payment(image_file, expected_amount):
    try:
        # Convert uploaded image to NumPy array
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Error: Could not load the image.")

        # Preprocess the image for better OCR
        processed_image = preprocess_image(image)

        # Perform OCR
        extracted_text = pytesseract.image_to_string(processed_image)
        extracted_text = extracted_text.lower()  # Normalize text for better matching

        print(f"\n📜 Extracted Text:\n{extracted_text}\n")

        # Extract and validate UTR ID
        utr_id = extract_utr(extracted_text)
        if not utr_id:
            return "❌ No valid UTR found", False

        # Validate recipient
        # if "jitendra choudhary" not in extracted_text:
        #     return "❌ Invalid recipient"


        # Extract and validate amount
        extracted_amount, valid_amount = extract_amount(extracted_text, expected_amount)
        print(f"Amount Extracted: {extracted_amount}")
        print(f"Amount Valid: {valid_amount}")
        if not valid_amount:
            return f"❌ Incorrect amount. Expected: ₹{expected_amount}, Found: {extracted_amount}", False
        
        # Extract and validate transaction time
        extracted_time, valid_time = extract_time(extracted_text)
        print(f"Extracted Time: {extracted_time}")
        print(f"Valid Time: {valid_time}")
        if not valid_time:
            return f"❌ Invalid transaction time. Extracted: {extracted_time}", False

        # ✅ If all checks pass, return UTR ID
        return f"✅ Payment Verified! UTR: {utr_id}, Amount: ₹{extracted_amount}, Time: {extracted_time}", True

    except Exception as e:
        print(f"⚠️ Error processing payment image: {e}")
        return "⚠️ Error in processing"

