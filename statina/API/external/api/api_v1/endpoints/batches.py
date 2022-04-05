from fastapi import APIRouter, Depends, Request
from starlette.responses import RedirectResponse


from statina.adapter import StatinaAdapter
from statina.API.external.api.deps import get_current_user
from statina.config import get_nipt_adapter, email_settings
from statina.models.database import User

router = APIRouter()


@router.get("/", deprecated=True)
def batches(
    request: Request,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """List of all batches"""
    return RedirectResponse(email_settings.website_uri)
