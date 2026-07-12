from pathlib import Path

from services.document_extractor import _prepare_raw_files_for_vision, extract_all


def test_pdf_extraction_includes_text_not_just_acroform():
    pdf_path = Path(__file__).resolve().parent.parent.parent / "data" / "Example_G-28.pdf"
    data = pdf_path.read_bytes()
    docs = extract_all([("Example_G-28.pdf", data)])

    assert len(docs) == 1
    text = docs[0].text

    # Acroform values should still be present
    assert "Pt3Line5a_FamilyName[1]: Smith" in text
    assert "b.smith_00@test.ai" in text

    # Widget annotation extraction (broken AcroForm tree misses these via get_fields)
    assert "Pt2Line1b_BarNumber[0]: 12083456" in text
    assert "Pt2Line1a_LicensingAuthority[0]: State Bar of California" in text
    assert "immigration@tryalma.ai" in text

    # Full page text should also be included (was previously skipped)
    assert "### Extracted Text" in text
    assert "Form G-28" in text
    assert len(text) > 1000


def test_prepare_raw_files_for_vision_skips_text_extraction():
    pdf_path = Path(__file__).resolve().parent.parent.parent / "data" / "Example_G-28.pdf"
    data = pdf_path.read_bytes()
    vision_items = _prepare_raw_files_for_vision([("Example_G-28.pdf", data)])

    assert len(vision_items) > 0
    assert all(mime == "image/png" for mime, _ in vision_items)
