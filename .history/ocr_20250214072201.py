from PyPDF2 import PdfReader
import re

def extract_payment_info(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # Nový slovník pro všechna data
        extracted_data = {
            # Pojištěnec
            "pojistenecjmeno": None,
            "pojistenecprijmeni": None,
            "pojistenecrc": None,
            
            # Žadatel
            "zadateljmeno": None,
            "zadatelprijmeni": None,
            "zadateltelefon": None,
            
            # Komunikace
            "komunikacezpusob": None,
            "komunikaceadresa": None,
            "komunikacedatschranka": None,
            "komunikaceemail": None,
            
            # Bankovní údaje
            "preplatekbankapredcisli": None,
            "preplatekbankacislouctu": None,
            "preplatekbankakodbanky": None,
            "preplatekslozenkaadr": None,
            
            # Ostatní
            "typnamitky": None,
            "popis": None,
            "datumpodani": None
        }

        # Regex patterns pro nová data
        patterns = {
            # Pojištěnec
            "pojistenec_rc": r'(?:číslo pojištěnce|rodné číslo):\s*(\d{6}\/?\d{3,4})',
            
            # Bankovní účet - zachováváme váš původní pattern
            "bank_account": r'(?:účet|číslo účtu)?:?\s*(?:(\d+)-)?(\d+)\/(\d{4})',
            
            # Kontaktní údaje
            "telefon": r'(?:tel|telefon|kontakt):\s*([+\d\s-]{9,})',
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "datova_schranka": r'(?:DS|datová schránka):\s*([a-zA-Z0-9]{7})',
            
            # Adresa
            "adresa": r'(?:adresa|bydliště):\s*([^\n]+)',
            
            # Datum
            "datum": r'(?:dne|datum):\s*(\d{1,2}\.\s*\d{1,2}\.\s*\d{4})',
            
            # Popis námitky
            "popis": r'(?:popis|text námitky):\s*([^\n]+(?:\n[^\n]+)*)'
        }

        # Procházení patterns a extrakce dat
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if key == "bank_account":
                    # Rozdělení čísla účtu
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

        # Zpracování jmen
        jmeno_match = re.search(r'jméno[^:]*:\s*([^\n]+)', text, re.IGNORECASE)
        if jmeno_match:
            full_name = jmeno_match.group(1).strip().split()
            if len(full_name) >= 2:
                extracted_data["pojistenecjmeno"] = full_name[0]
                extracted_data["pojistenecprijmeni"] = " ".join(full_name[1:])

        return extracted_data

    except Exception as e:
        return {"error": f"Chyba při zpracování PDF: {str(e)}"}