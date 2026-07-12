from schemas.form_fields import FormField
from services.form_schema import build_json_schema


def test_build_json_schema_from_fields():
    fields = [
        FormField(
            name="family-name",
            label="2.a. Family Name (Last Name)",
            field_type="text",
        ),
        FormField(
            name="passport-sex",
            label="6. Sex",
            field_type="select",
            options=["M", "F", "X"],
        ),
    ]
    schema = build_json_schema(fields)
    assert schema["type"] == "object"
    assert "family-name" in schema["properties"]
    assert schema["properties"]["family-name"]["type"] == ["string", "null"]
    assert schema["properties"]["passport-sex"]["enum"] == ["M", "F", "X", None]
    assert set(schema["required"]) == {"family-name", "passport-sex"}
    assert schema["additionalProperties"] is False


def test_normalize_field_type():
    from services.playwright_service import _normalize_field_type

    assert _normalize_field_type("text", False) == "text"
    assert _normalize_field_type("checkbox", True) == "checkbox_group"
    assert _normalize_field_type("select-one", False) == "select"
