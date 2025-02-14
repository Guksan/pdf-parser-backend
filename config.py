import os
from dotenv import load_dotenv

load_dotenv()

OCR_LANG = os.getenv("OCR_LANG", "eng")  # Jazyk OCR
UPLOAD_FOLDER = "uploads"
