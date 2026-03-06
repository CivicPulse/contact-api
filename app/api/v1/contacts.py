from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ContactSubmission
from app.db.session import get_db
from app.schemas.contact import ContactCreate, ContactResponse

router = APIRouter()


def _get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    payload: ContactCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ContactSubmission:
    submission = ContactSubmission(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        message=payload.message,
        client_ip=_get_client_ip(request),
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission
