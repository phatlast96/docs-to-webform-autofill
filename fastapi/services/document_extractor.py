import base64
import io
from dataclasses import dataclass

import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from pypdf import PdfReader


@dataclass
class ExtractedDocument:
    filename: str
    mime_type: str
    text: str
    image_b64: str | None = None


def _guess_image_mime(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:2] == b"\xff\xd8":
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/png"


def _extract_pdf_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    if reader.get_fields():
        parts = [f"{k}: {v.get('/V', '')}" for k, v in reader.get_fields().items()]
        if any(parts):
            return "\n".join(str(p) for p in parts)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if text.strip():
        return text
    images = convert_from_bytes(data)
    return "\n".join(pytesseract.image_to_string(img) for img in images)


def _extract_image_text(data: bytes) -> tuple[str, str]:
    img = Image.open(io.BytesIO(data))
    text = pytesseract.image_to_string(img)
    b64 = base64.b64encode(data).decode()
    return text, b64


def extract_all(files: list[tuple[str, bytes]]) -> list[ExtractedDocument]:
    results: list[ExtractedDocument] = []
    for filename, data in files:
        if data[:4] == b"%PDF":
            results.append(
                ExtractedDocument(
                    filename=filename,
                    mime_type="application/pdf",
                    text=_extract_pdf_text(data),
                )
            )
        else:
            text, b64 = _extract_image_text(data)
            results.append(
                ExtractedDocument(
                    filename=filename,
                    mime_type=_guess_image_mime(data),
                    text=text,
                    image_b64=b64,
                )
            )
    return results
