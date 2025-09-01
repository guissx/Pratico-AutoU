from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.services.replyService import classify_email

app = FastAPI(
    title="Classificador de E-mails (Produtivo vs Improdutivo)",
    description="Recebe PDF/TXT, faz NLP (preprocess service), classifica (messaging service) e sugere resposta.",
    version="1.0.0",
)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition","Content-Type"], 
)

class ClassifyResponse(BaseModel):
    category: str
    confidence: float
    suggested_reply: str
    language: str
    preview: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/classify", response_model=ClassifyResponse)
async def classify(
    file: UploadFile = File(...),
    stemming: Optional[bool] = False,
    provider: Optional[str] = "openai"
):
    filename = (file.filename or "").lower()
    if not (filename.endswith(".pdf") or filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Envie um arquivo .pdf ou .txt")

    data = await file.read()
    try:
        result = classify_email(filename, data, provider=provider, stemming=bool(stemming))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return JSONResponse(content=ClassifyResponse(**result).model_dump())

