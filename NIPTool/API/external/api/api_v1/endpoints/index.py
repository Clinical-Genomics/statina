from fastapi import APIRouter, Request
from NIPTool.config import templates

router = APIRouter()


@router.post("/")
def index(request: Request):
    """Log in view."""

    return templates.TemplateResponse("index.html", context={"request": request})


@router.get("/")
def index(request: Request):
    """Log in view."""

    return templates.TemplateResponse(
        "index.html", context={"request": request, "current_user": ""}
    )
