from fastapi import APIRouter, Request
from NIPTool.config import templates

router = APIRouter()


@router.post("/")
def index(request: Request):
    """Log in view."""
    return templates.TemplateResponse(
        "index.html", context={"request": request, "current_user": ""}
    )


@router.get("/")
def index(request: Request):
    """Log in view."""
    return templates.TemplateResponse(
        "index.html", context={"request": request, "current_user": ""}
    )


@router.get("/new_user")
def new_user(request: Request):
    """Log in view."""
    return templates.TemplateResponse(
        "new_user.html", context={"request": request, "current_user": ""}
    )


@router.post("/new_user")
def new_user(request: Request):
    """Log in view."""
    return templates.TemplateResponse(
        "new_user.html",
        context={
            "request": request,
            "current_user": "",
            "user_info": request.cookies.get("user_info"),
        },
    )
