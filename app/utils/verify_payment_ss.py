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

        # Debugging: Print extracted text
        print(f"\nExtracted Text:\n{extracted_text}\n")

        # Define UTR/Transaction ID patterns
        utr_patterns = [
            r"\b\d{12}\b",  # 12-digit UTRs
            r"\b[A-Z0-9]{16,22}\b",  # Some UTRs contain letters & are longer
        ]

        # Search for UTR ID
        for pattern in utr_patterns:
            match = re.search(pattern, extracted_text)
            if match:
                return match.group()  # Return the first UTR found

        return ""

    except Exception as e:
        print(f"Error processing payment image: {e}")
        return "Error in processing"
