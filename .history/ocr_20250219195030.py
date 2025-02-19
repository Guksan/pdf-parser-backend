from PyPDF2 import PdfReader
import re
import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
import shutil

# Načtení proměnných prostředí
load_dotenv()

OCR_LANG = os.getenv("OCR_LANG", "eng")  # Jazyk OCR
UPLOAD_FOLDER = "uploads"

# Vytvoření složky pro nahrané soubory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()

def extract_payment_info(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        extracted_data = {
            "pojistenecjmeno": None,
            "pojistenecprijmeni": None,
            "pojistenecrc": None,
            "zadateljmeno": None,
            "zadatelprijmeni": None,
            "zadateltelefon": None,
            "komunikacezpusob": None,
            "komunikaceadresa": None,
            "komunikacedatschranka": None,
            "komunikaceemail": None,
            "preplatekbankapredcisli": None,
            "preplatekbankacislouctu": None,
            "preplatekbankakodbanky": None,
            "preplatekslozenkaadr": None,
            "typnamitky": None,
            "popis": None,
            "datumpodani": None
        }

        patterns = {
            "pojistenec_rc": r'(?:číslo pojištěnce|rodné číslo):\s*(\d{6}\/?\d{3,4})',
            "bank_account": r'(?:účet|číslo účtu)?:?\s*(?:(\d+)-)?(\d+)\/(\d{4})',
            "telefon": r'(?:tel|telefon|kontakt):\s*([+\d\s-]{9,})',
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "datova_schranka": r'(?:DS|datová schránka):\s*([a-zA-Z0-9]{7})',
            "adresa": r'(?:adresa|bydliště):\s*([^\n]+)',
            "datum": r'(?:dne|datum):\s*(\d{1,2}\.\s*\d{1,2}\.\s*\d{4})',
            "popis": r'(?:popis|text námitky):\s*([^\n]+(?:\n[^\n]+)*)'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if key == "bank_account":
                    extracted_data["preplatekbankapredcisli"] = match.group(1) if match.group(1) else None
                    extracted_data["preplatekbankacislouctu"] = match.group(2)
                    extracted_data["preplatekbankakodbanky"] = match.group(3)
                elif key == "pojistenec_rc":
                    extracted_data["pojistenecrc"] = match.group(1)
                elif key == "telefon":
                    extracted_data["zadateltelefon"] = match.group(1).replace(" ", "")
                elif key == "email":
                    extracted_data["komunikaceemail"] = match.group(0)
                elif key == "datova_schranka":
                    extracted_data["komunikacedatschranka"] = match.group(1)
                elif key == "adresa":
                    extracted_data["komunikaceadresa"] = match.group(1).strip()
                elif key == "datum":
                    extracted_data["datumpodani"] = match.group(1)
                elif key == "popis":
                    extracted_data["popis"] = match.group(1).strip()

        return extracted_data

    except Exception as e:
        return {"error": f"Chyba při zpracování PDF: {str(e)}"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    data = extract_payment_info(file_path)

    return {"parsed_data": data}
