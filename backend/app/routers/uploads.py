import os
import uuid
from typing import Literal
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from ..models.schemas import UploadResponse
from ..core.config import settings

router = APIRouter()

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage")
STORAGE_DIR = os.path.abspath(os.path.join(STORAGE_DIR))

os.makedirs(STORAGE_DIR, exist_ok=True)

@router.post("", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["png", "jpg", "jpeg", "pdf"]:
        raise HTTPException(status_code=400, detail="Formatos permitidos: png, jpg, jpeg, pdf")

    fname = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(STORAGE_DIR, fname)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    url = f"/static/{fname}"
    return UploadResponse(file_url=url, type="pdf" if ext == "pdf" else "image")
