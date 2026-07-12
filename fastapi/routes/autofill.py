from fastapi import APIRouter, File, HTTPException, UploadFile

from schemas.autofill import AutofillResponse
from services.autofill_service import run_autofill

router = APIRouter()


@router.post("/autofill", response_model=AutofillResponse)
async def autofill(
    images: list[UploadFile] = File(default=[]),
    pdfs: list[UploadFile] = File(default=[]),
) -> AutofillResponse:
    if not images and not pdfs:
        raise HTTPException(400, "Upload at least one image or PDF")

    files: list[tuple[str, bytes]] = []
    for img in images:
        files.append((img.filename or "image", await img.read()))
    for pdf in pdfs:
        files.append((pdf.filename or "document.pdf", await pdf.read()))

    return await run_autofill(files)
