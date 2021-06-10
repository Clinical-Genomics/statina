from fastapi import APIRouter, Request

from statina.config import templates

router = APIRouter()


@router.post("/")
def index(request: Request):
    """Log in view."""
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "current_user": "",
            "info_type": request.cookies.get("info_type"),
            "user_info": request.cookies.get("user_info"),
        },
    )


@router.get("/")
def index(request: Request):
    """Log in view."""
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "current_user": "",
            "info_type": request.cookies.get("info_type"),
            "user_info": request.cookies.get("user_info"),
        },
    )
