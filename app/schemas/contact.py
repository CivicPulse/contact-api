import re
import unicodedata
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

_PHONE_RE = re.compile(r"^[0-9+\-().\ ]{7,30}$")


def _clean(value: str, *, allow_newlines: bool = False) -> str:
    """Strip whitespace and remove control characters."""
    cleaned = []
    for ch in value:
        cat = unicodedata.category(ch)
        if cat.startswith("C"):
            if allow_newlines and ch in ("\n", "\r"):
                cleaned.append(ch)
        else:
            cleaned.append(ch)
    return "".join(cleaned).strip()


class ContactCreate(BaseModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    message: str | None = Field(default=None, max_length=5000)

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def sanitize_name(cls, v: object) -> object:
        if not isinstance(v, str):
            return v
        v = _clean(v)
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def sanitize_phone(cls, v: object) -> object:
        if not isinstance(v, str):
            return v
        v = _clean(v)
        if not v:
            return None
        if not _PHONE_RE.match(v):
            raise ValueError("invalid phone format")
        return v

    @field_validator("message", mode="before")
    @classmethod
    def sanitize_message(cls, v: object) -> object:
        if not isinstance(v, str):
            return v
        v = _clean(v, allow_newlines=True)
        return v or None

    @model_validator(mode="after")
    def require_email_or_phone(self) -> "ContactCreate":
        if not self.email and not self.phone:
            raise ValueError("At least one of email or phone must be provided.")
        return self


class ContactResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    message: str | None
    client_ip: str | None
    submitted_at: datetime

    model_config = {"from_attributes": True}
