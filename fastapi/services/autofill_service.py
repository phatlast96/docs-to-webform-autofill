from schemas.autofill import AutofillResponse
from services.document_extractor import extract_all
from services.form_schema import build_json_schema, format_fields_for_prompt
from services.openai_client import extract_form_values
from services.playwright_service import extract_form_schema, fill_form
from services.prompts import build_autofill_prompt


async def run_autofill(files: list[tuple[str, bytes]]) -> AutofillResponse:
    # Step 1: Extract web form inputs (work backwards)
    form_schema = await extract_form_schema()

    # Step 2: Build structured output schema from extracted fields
    json_schema = build_json_schema(form_schema.fields)

    # Step 3: Extract document content
    docs = extract_all(files)
    document_text = "\n\n".join(f"### {d.filename}\n{d.text}" for d in docs)
    image_b64_list = [(d.mime_type, d.image_b64) for d in docs if d.image_b64]

    # Step 4: Build LLM prompt (fields + full page HTML + document text)
    prompt = build_autofill_prompt(
        form_fields_text=format_fields_for_prompt(form_schema.fields),
        page_html=form_schema.page_html,
        document_text=document_text,
    )

    # Step 5: OpenAI structured output
    llm_output = extract_form_values(prompt, json_schema, image_b64_list)

    # Step 6: Playwright fill form
    fill_result = await fill_form(llm_output)

    return AutofillResponse(
        form_field_count=len(form_schema.fields),
        llm_output=llm_output,
        fill_result=fill_result,
    )
