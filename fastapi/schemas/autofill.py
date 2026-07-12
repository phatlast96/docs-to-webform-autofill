from pydantic import BaseModel


class AutofillResponse(BaseModel):
    form_field_count: int
    llm_output: dict
    fill_result: dict
    input_tokens: int
    output_tokens: int
