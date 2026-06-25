import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from shared_planner.api.auth import CurrentAdmin
from shared_planner.planning_export import build_planning_ods

router = APIRouter(prefix="/export", tags=["export"])

ODS_MEDIA_TYPE = "application/vnd.oasis.opendocument.spreadsheet"


@router.get("/planning/{range_mode}", dependencies=[Depends(CurrentAdmin)])
def export_planning(range_mode: str) -> StreamingResponse:
    """Download the planning of all shops as a formatted ODS workbook.

    ``range_mode`` is one of ``week``, ``fortnight`` or ``all`` (until the last
    reservation).
    """
    content = build_planning_ods(range_mode)
    stamp = datetime.date.today().strftime("%Y%m%d")
    filename = f"planning_{range_mode}_{stamp}.ods"
    return StreamingResponse(
        iter([content]),
        media_type=ODS_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
