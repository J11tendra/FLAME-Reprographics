import os
import cv2
import pytesseract
import re
import numpy as np
import numpy as np
import cv2
import pytesseract
import re

def verify_payment(image_file):
    try:
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Error: Could not load the image.")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        extracted_text = pytesseract.image_to_string(gray).strip()
        print(extracted_text)

        utr_id = None
        utr_patterns = [
            r"\b\d{12}\b", 
            r"\b[A-Z0-9]{16,22}\b",
        ]
        for pattern in utr_patterns:
            match = re.search(pattern, extracted_text)
            if match:
                utr_id = match.group()
                print(f"UTR FOUND: {utr_id}")
                break

        date_match = None
        date_patterns = [
            r"\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}\b",
            r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b",
        ]
        for pat in date_patterns:
            m = re.search(pat, extracted_text, flags=re.IGNORECASE)
            if m:
                date_match = m.group()
                print(f"DATE FOUND: {date_match}")
                break

        return (utr_id, date_match)

    except Exception as e:
        print(f"Error processing payment image: {e}")
        return (None, None)