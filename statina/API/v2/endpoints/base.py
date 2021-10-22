from fastapi import APIRouter
from starlette.responses import JSONResponse
from statina.constants import SCOPES

router = APIRouter(prefix="/v2")


@router.get("/")
def base():
    """Landing page"""
    return JSONResponse("Welcome to Statina!")


@router.get("/scopes")
def scopes():
    """API scopes"""
    return SCOPES
