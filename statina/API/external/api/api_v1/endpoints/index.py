from fastapi import APIRouter
from starlette.responses import RedirectResponse

from statina.config import settings

router = APIRouter()


@router.get("/", deprecated=True)
def index():
    """Log in view."""
    return RedirectResponse(settings.website_uri)
