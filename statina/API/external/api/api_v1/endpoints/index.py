from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse

from statina.config import email_settings

router = APIRouter()


@router.get("/", deprecated=True)
def index(request: Request):
    """Log in view."""
    return RedirectResponse(email_settings.website_uri)
