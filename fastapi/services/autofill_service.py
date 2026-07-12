from datetime import datetime, timezone
from pathlib import Path

from config import settings
from schemas.autofill import AutofillResponse
from services.document_extractor import _prepare_raw_files_for_vision, prepare_documents
from services.form_schema import build_json_schema, format_fields_for_prompt
from services.openai_client import extract_form_values
from services.playwright_service import extract_form_schema, fill_form
from services.prompts import AUTOFILL_SYSTEM, build_autofill_prompt

PROMPT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "prompt-output"


def _write_prompt_debug(prompt: str) -> Path:
    """Write the interpolated prompt to prompt-output/ for debugging."""
    PROMPT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = PROMPT_OUTPUT_DIR / f"autofill-prompt-{stamp}.txt"
    path.write_text(
        f"=== SYSTEM ===\n{AUTOFILL_SYSTEM}\n\n=== USER ===\n{prompt}\n",
        encoding="utf-8",
    )
    return path


async def run_autofill(
    files: list[tuple[str, bytes]],
    *,
    use_raw_documents: bool = False,
) -> AutofillResponse:
    # Step 1: Extract web form inputs (work backwards)
    form_schema = await extract_form_schema()

    # Step 2: Build structured output schema from extracted fields
    json_schema = build_json_schema(form_schema.fields)

    # Step 3: Prepare document content for LLM
    if use_raw_documents:
        document_text = ""
        image_b64_list = _prepare_raw_files_for_vision(files)
    else:
        document_text, image_b64_list = prepare_documents(files)

    # Step 4: Build LLM prompt (fields + full page HTML + document content)
    prompt = build_autofill_prompt(
        form_fields_text=format_fields_for_prompt(form_schema.fields),
        page_html=form_schema.page_html,
        document_text=document_text,
        use_raw_documents=use_raw_documents,
    )

    if settings.debug:
        debug_path = _write_prompt_debug(prompt)
        print(f"Wrote prompt debug output to {debug_path}")

    # Step 5: OpenAI structured output
    extraction = extract_form_values(prompt, json_schema, image_b64_list)

    # Step 6: Playwright fill form
    fill_result = await fill_form(extraction.llm_output)

    return AutofillResponse(
        form_field_count=len(form_schema.fields),
        llm_output=extraction.llm_output,
        fill_result=fill_result,
        input_tokens=extraction.input_tokens,
        output_tokens=extraction.output_tokens,
    )
