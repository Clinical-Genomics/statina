from fastapi import APIRouter
from starlette.responses import RedirectResponse

from statina.config import email_settings

router = APIRouter()


@router.get("/", deprecated=True)
def index():
    """Log in view."""
    return RedirectResponse(email_settings.website_uri)
