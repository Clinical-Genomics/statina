
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from NIPTool.schemas.server.user import User, Token
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from NIPTool.server.web_app.api.deps import get_current_active_user, authenticate_user, create_access_token, temp_get_config
from datetime import timedelta
templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/")
def index(request: Request):
    """Log in view."""
    #user = session.get("user")
    #if user or app.config.get("LOGIN_DISABLED"):
    #    return redirect(url_for("server.batches"))
    return templates.TemplateResponse("index.html", context={"request": request})
