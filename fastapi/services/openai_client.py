import json

from openai import OpenAI

from config import settings
from services.prompts import AUTOFILL_SYSTEM

client = OpenAI(api_key=settings.openai_api_key)


def extract_form_values(
    prompt: str,
    json_schema: dict,
    image_b64_list: list[tuple[str, str]],
) -> dict:
    content: list[dict] = [{"type": "text", "text": prompt}]
    for mime, b64 in image_b64_list:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            }
        )

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": AUTOFILL_SYSTEM},
            {"role": "user", "content": content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "form_autofill_response",
                "strict": True,
                "schema": json_schema,
            },
        },
    )
    return json.loads(response.choices[0].message.content)
