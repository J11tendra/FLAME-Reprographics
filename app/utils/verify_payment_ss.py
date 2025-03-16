import os
import cv2
import pytesseract
import re
import numpy as np
import numpy as np
import cv2
import pytesseract
import re
from datetime import datetime, timedelta


def verify_payment(image_file):
    try:
        # Convert uploaded image to NumPy array
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Error: Could not load the image.")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding for better OCR accuracy
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # Perform OCR
        extracted_text = pytesseract.image_to_string(gray)

        print(f"\nExtracted Text:\n{extracted_text}\n")

        utr_patterns = [
            r"\b\d{12}\b",  # 12-digit UTRs
            r"\b[A-Z0-9]{16,22}\b",  # Some UTRs contain letters & are longer
        ]

        # Search for UTR ID
        # for pattern in utr_patterns:
        #     match = re.search(pattern, extracted_text)
        #     if match:
        #         return match.group()  # Return the first UTR found

        # return ""
    
         # Extract UTR
        utr_id = None
        for pattern in utr_patterns:
            match = re.search(pattern, extracted_text)
            if match:
                utr_id = match.group()
                break  # Stop at the first match

        if not utr_id:
            return "No valid UTR found"

        # **Check for the "To" field**
        if "flame university" not in extracted_text.lower():
            return "Invalid recipient"

        # **Check transaction time (within last 5 minutes)**
        time_patterns = [
            r"(\d{2}:\d{2}(?:\s?[APap][Mm])?)",  # Match time format like "14:30" or "2:30 PM"
            r"(\d{2}-\d{2}-\d{4}\s\d{2}:\d{2})"  # Format "DD-MM-YYYY HH:MM"
        ]

        now = datetime.now()
        valid_time = False

        for pattern in time_patterns:
            time_match = re.search(pattern, extracted_text)
            if time_match:
                try:
                    extracted_time_str = time_match.group(1)
                    extracted_time = datetime.strptime(extracted_time_str, "%H:%M")

                    # Calculate time difference
                    time_diff = now - extracted_time
                    if timedelta(minutes=-5) <= time_diff <= timedelta(minutes=5):
                        valid_time = True
                        break
                except ValueError:
                    continue  # Skip invalid time formats

        if not valid_time:
            return "Transaction time out of valid window"

        # If both conditions are met, return the UTR
        return utr_id

    except Exception as e:
        print(f"Error processing payment image: {e}")
        return "Error in processing"
