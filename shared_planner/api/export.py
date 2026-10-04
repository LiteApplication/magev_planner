import datetime
import re
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from shared_planner.api.auth import CurrentAdmin
from shared_planner.planning_export import build_planning_ods

router = APIRouter(prefix="/export", tags=["export"])

ODS_MEDIA_TYPE = "application/vnd.oasis.opendocument.spreadsheet"


@router.get("/planning/{range_mode}", dependencies=[Depends(CurrentAdmin)])
def export_planning(
    range_mode: str,
    start: str | None = None,
    end: str | None = None,
    group: str | None = None,
) -> StreamingResponse:
    """Download the planning of all shops as a formatted ODS workbook.

    ``range_mode`` is one of ``week``, ``fortnight`` or ``all`` (until the last
    reservation). Passing ``start`` and ``end`` (``YYYY-MM-DD``) exports that
    explicit period instead. ``group`` limits the export to a single group.
    """
    if range_mode not in ("week", "fortnight", "all"):
        raise HTTPException(status_code=400, detail="error.export.invalid_params")
    if (start is None) != (end is None):
        raise HTTPException(status_code=400, detail="error.export.invalid_params")
    if start is not None and end is not None:
        try:
            start_date = datetime.date.fromisoformat(start)
            end_date = datetime.date.fromisoformat(end)
        except ValueError:
            raise HTTPException(status_code=400, detail="error.export.invalid_params")
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="error.export.invalid_params")
    content = build_planning_ods(range_mode, start=start, end=end, group=group)
    stamp = datetime.date.today().strftime("%Y%m%d")
    label = group.replace(" ", "-") if group else range_mode
    filename = f"planning_{label}_{stamp}.ods"
    # ASCII fallback for old clients plus the RFC 5987 UTF-8 form.
    ascii_name = re.sub(r"[^A-Za-z0-9._-]", "_", filename.encode("ascii", "ignore").decode())
    disposition = (
        f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{quote(filename, safe="")}'
    )
    return StreamingResponse(
        iter([content]),
        media_type=ODS_MEDIA_TYPE,
        headers={"Content-Disposition": disposition},
    )
