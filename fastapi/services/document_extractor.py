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


def _extract_pdf_widget_fields(reader: PdfReader) -> list[str]:
    """Extract filled values from page widget annotations.

    pypdf's get_fields() misses most values when the AcroForm tree is broken.
    Walking /Annots widgets is more reliable for PDFs like USCIS G-28.
    """
    lines: list[str] = []
    skip_values = {"", "N/A", "/Off"}

    for page in reader.pages:
        annots = page.get("/Annots")
        if not annots:
            continue
        annots = annots.get_object()
        for annot_ref in annots:
            annot = annot_ref.get_object()
            if annot.get("/Subtype") != "/Widget":
                continue
            name = annot.get("/T")
            if not name:
                continue
            val = annot.get("/V")
            if val is None:
                val = annot.get("/DV")
            if val is None:
                continue
            val_str = str(val).strip()
            if val_str in skip_values:
                continue
            lines.append(f"{name}: {val_str}")
    return lines


def _extract_pdf_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    sections: list[str] = []

    widget_lines = _extract_pdf_widget_fields(reader)
    if widget_lines:
        sections.append("### Form Fields\n" + "\n".join(widget_lines))

    text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if text:
        sections.append("### Extracted Text\n" + text)

    if sections:
        return "\n\n".join(sections)

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


def _prepare_raw_files_for_vision(
    files: list[tuple[str, bytes]],
) -> list[tuple[str, str]]:
    """Send raw images and PDF pages to vision — no OCR or text extraction."""
    vision_items: list[tuple[str, str]] = []
    for filename, data in files:
        if data[:4] == b"%PDF":
            for page_num, img in enumerate(convert_from_bytes(data), start=1):
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                vision_items.append(("image/png", b64))
        else:
            mime = _guess_image_mime(data)
            b64 = base64.b64encode(data).decode()
            vision_items.append((mime, b64))
    return vision_items


def prepare_documents(
    files: list[tuple[str, bytes]],
) -> tuple[str, list[tuple[str, str]]]:
    docs = extract_all(files)
    document_text = "\n\n".join(f"### {d.filename}\n{d.text}" for d in docs)
    image_b64_list = [(d.mime_type, d.image_b64) for d in docs if d.image_b64]
    return document_text, image_b64_list
