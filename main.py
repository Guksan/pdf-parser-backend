from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from ocr import extract_payment_info

app = FastAPI()

# CORS - přidáme URL 4FD platformy
app.add_middleware(
   CORSMiddleware,
   allow_origins=[
       "http://localhost:3000",  # pro lokální vývoj
       "https://pdf-parser-frontend.onrender.com", # pro produkci
       "*"  # pro 4FD platformu (v produkci by mělo být konkrétnější)
   ],
   allow_credentials=True, 
   allow_methods=["*"],
   allow_headers=["*"],
)

# Vytvoření složky pro uploady
os.makedirs("uploads", exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
   try:
       # Uložení souboru
       file_path = f"uploads/{file.filename}"
       
       with open(file_path, "wb") as buffer:
           content = await file.read()  # Změna na async čtení
           buffer.write(content)
       
       # Extrakce dat
       data = extract_payment_info(file_path)
       
       # Vymazání dočasného souboru
       os.remove(file_path)
       
       # Odpověď s novými poli
       return {
           "filename": file.filename,
           "data": {
               # Pojištěnec
               "pojistenecjmeno": data.get("pojistenecjmeno"),
               "pojistenecprijmeni": data.get("pojistenecprijmeni"),
               "pojistenecrc": data.get("pojistenecrc"),
               
               # Žadatel
               "zadateljmeno": data.get("zadateljmeno"),
               "zadatelprijmeni": data.get("zadatelprijmeni"),
               "zadateltelefon": data.get("zadateltelefon"),
               
               # Komunikace
               "komunikacezpusob": data.get("komunikacezpusob"),
               "komunikaceadresa": data.get("komunikaceadresa"),
               "komunikacedatschranka": data.get("komunikacedatschranka"),
               "komunikaceemail": data.get("komunikaceemail"),
               
               # Bankovní údaje
               "preplatekbankapredcisli": data.get("preplatekbankapredcisli"),
               "preplatekbankacislouctu": data.get("preplatekbankacislouctu"),
               "preplatekbankakodbanky": data.get("preplatekbankakodbanky"),
               "preplatekslozenkaadr": data.get("preplatekslozenkaadr"),
               
               # Ostatní
               "typnamitky": data.get("typnamitky"),
               "popis": data.get("popis"),
               "datumpodani": data.get("datumpodani")
           }
       }
       
   except Exception as e:
       return {"error": str(e)}

if __name__ == "__main__":
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8000)