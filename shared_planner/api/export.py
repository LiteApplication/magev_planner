import datetime

from fastapi import APIRouter, Depends
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
    content = build_planning_ods(range_mode, start=start, end=end, group=group)
    stamp = datetime.date.today().strftime("%Y%m%d")
    label = group.replace(" ", "-") if group else range_mode
    filename = f"planning_{label}_{stamp}.ods"
    return StreamingResponse(
        iter([content]),
        media_type=ODS_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
