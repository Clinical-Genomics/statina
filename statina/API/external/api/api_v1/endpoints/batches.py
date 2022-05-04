from fastapi import APIRouter
from starlette.responses import RedirectResponse


from statina.config import settings


router = APIRouter()


@router.get("/", deprecated=True)
def batches():
    """List of all batches"""
    return RedirectResponse(settings.website_uri)
