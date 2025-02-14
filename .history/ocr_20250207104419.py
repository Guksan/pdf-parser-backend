from PyPDF2 import PdfReader
import re

def extract_payment_info(file_path):
    try:
        # Načtení PDF
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # Slovník pro uložení platebních údajů
        payment_info = {
            "cislo_faktury": None,
            "cislo_uctu": None,
            "banka": None,
            "castka": None,
            "variabilni_symbol": None,
            "datum_splatnosti": None,
            "dodavatel": None,
            "odberatel": None
        }

        # Extrakce pomocí regulárních výrazů a hledání v textu
        # Číslo účtu
        ucet_match = re.search(r'(\d{9,10})\/(\d{4})', text)
        if ucet_match:
            payment_info["cislo_uctu"] = ucet_match.group(1)
            payment_info["banka"] = ucet_match.group(2)

        # Částka
        castka_match = re.search(r'Celkem k úhradě\s*(\d+[\s,]*\d*,\d{2})', text)
        if castka_match:
            payment_info["castka"] = castka_match.group(1).replace(" ", "")

        # Variabilní symbol
        vs_match = re.search(r'Variabilní symbol\s*(\d+)', text)
        if vs_match:
            payment_info["variabilni_symbol"] = vs_match.group(1)

        # Číslo faktury
        faktura_match = re.search(r'FAKTURA č\.\s*(\d+)', text)
        if faktura_match:
            payment_info["cislo_faktury"] = faktura_match.group(1)

        # Datum splatnosti
        splatnost_match = re.search(r'Datum splatnosti\s*(\d{1,2}\.\s*\d{1,2}\.\s*\d{4})', text)
        if splatnost_match:
            payment_info["datum_splatnosti"] = splatnost_match.group(1)

        # Dodavatel
        dodavatel_match = re.search(r'DODAVATEL\s*([^\n]+)', text)
        if dodavatel_match:
            payment_info["dodavatel"] = dodavatel_match.group(1).strip()

        # Odběratel
        odberatel_match = re.search(r'ODBĚRATEL\s*([^\n]+)', text)
        if odberatel_match:
            payment_info["odberatel"] = odberatel_match.group(1).strip()

        return payment_info

    except Exception as e:
        return f"Chyba při zpracování PDF: {str(e)}"