from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from ocr import extract_payment_info

app = FastAPI()

# Povolení CORS pro komunikaci s frontendem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # adresa frontendu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vytvoření složky pro uploady, pokud neexistuje
os.makedirs("uploads", exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Uložení souboru
    file_path = f"uploads/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extrakce platebních informací
    payment_info = extract_payment_info(file_path)
    
    # Vrácení výsledku
    return {
        "filename": file.filename,
        "payment_info": payment_info
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)