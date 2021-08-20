from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/")
def index(request: Request):
    """Log in view."""
    return JSONResponse(
        content={
            "current_user": "",
            "info_type": request.cookies.get("info_type"),
            "user_info": request.cookies.get("user_info"),
        },
    )


@router.get("/")
def index(request: Request):
    """Log in view."""
    return JSONResponse(
        content={
            "current_user": "",
            "info_type": request.cookies.get("info_type"),
            "user_info": request.cookies.get("user_info"),
        },
    )
