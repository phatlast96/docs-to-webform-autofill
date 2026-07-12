AUTOFILL_SYSTEM = """You are a document data extraction assistant.
Given source documents and a target web form schema, extract matching field values.
Return only fields you are confident about. Use ISO dates (YYYY-MM-DD).
For select fields use exact option values. For checkbox groups return the value string.
Return null for unknown fields. Every field key must appear in the response."""


def build_autofill_prompt(
    form_fields_text: str,
    page_html: str,
    document_text: str,
) -> str:
    return f"""## Target Web Form Fields
{form_fields_text}

## Full Web Form Page HTML
The HTML below provides section headers, agreement text, and surrounding context
that individual field labels may not capture on their own.
{page_html}

## Extracted Document Text
{document_text}

## Instructions
Map information from the documents to the form fields listed above.
Use the field name as the JSON key and the extracted value as the value.
Refer to the page HTML for section context when deciding which document data maps to which field.
"""
