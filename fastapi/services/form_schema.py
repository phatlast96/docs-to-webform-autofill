from schemas.form_fields import FormField

_BASE_TYPE = {
    "text": "string",
    "tel": "string",
    "email": "string",
    "date": "string",
    "select": "string",
    "checkbox": "boolean",
    "checkbox_group": "string",
}


def build_json_schema(fields: list[FormField]) -> dict:
    properties: dict = {}
    for f in fields:
        base = _BASE_TYPE.get(f.field_type, "string")
        prop: dict = {"type": [base, "null"]}
        if f.field_type == "date":
            prop["description"] = "ISO date YYYY-MM-DD, or null if unknown"
        if f.options:
            prop["enum"] = f.options + [None]
        if f.label:
            prop["description"] = (
                prop.get("description", "") + f" — {f.label}"
            ).strip(" —")
        properties[f.name] = prop
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties.keys()),
        "additionalProperties": False,
    }


def format_fields_for_prompt(fields: list[FormField]) -> str:
    lines = []
    for f in fields:
        opts = f", options={f.options}" if f.options else ""
        lines.append(f"- {f.name} ({f.field_type}{opts}): {f.label}")
    return "\n".join(lines)
