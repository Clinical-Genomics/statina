from fastapi import APIRouter, Depends, Request
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.server.web_app.api.deps import get_nipt_adapter, get_current_active_user
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/batch_download/{batch_id}/{file_id}")
def batch_download(request: Request, batch_id: str, file_id: str, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """View for batch downloads"""

    batch = adapter.batch(batch_id)
    file_path = batch.get(file_id)

    if not validate_file_path(file_path):
        return redirect(request.referrer)

    file = Path(file_path)

    return send_from_directory(str(file.parent), file.name, as_attachment=True)


@router.post("/sample_download/{sample_id}/{file_id}")
def sample_download(request: Request, sample_id: str, file_id: str, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """View for sample downloads"""

    sample = adapter.sample(sample_id)
    file_path = sample.get(file_id)

    if not validate_file_path(file_path):
        return redirect(request.referrer)

    file = Path(file_path)

    return send_from_directory(str(file.parent), file.name, as_attachment=True)
