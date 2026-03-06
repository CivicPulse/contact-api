import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, model_validator


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    message: str

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
    message: str
    client_ip: str | None
    submitted_at: datetime

    model_config = {"from_attributes": True}
