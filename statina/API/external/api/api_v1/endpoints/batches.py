from fastapi import APIRouter
from starlette.responses import RedirectResponse


from statina.config import email_settings


router = APIRouter()


@router.get("/", deprecated=True)
def batches():
    """List of all batches"""
    return RedirectResponse(email_settings.website_uri)
