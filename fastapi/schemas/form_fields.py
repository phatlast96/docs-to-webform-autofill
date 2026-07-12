from pydantic import BaseModel, Field


class FormField(BaseModel):
    name: str
    label: str
    field_type: str  # text | tel | email | date | select | checkbox | checkbox_group
    options: list[str] = Field(default_factory=list)


class FormSchema(BaseModel):
    url: str
    fields: list[FormField]
    page_html: str
