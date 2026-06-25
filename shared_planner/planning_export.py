"""Generate a nicely formatted ODS planning export.

The workbook contains one sheet per shop with the weekly planning stacked
vertically (one block per week), plus a final "Contacts" sheet. Empty
volunteer places render as a to-fill cell with a dropdown whose entries are the
contact list, so the planning can be completed directly in a spreadsheet editor.

All wall-clock times follow the configured ``server_timezone`` setting: time
slots are stored as server-local wall-clock times, and reservation datetimes
(stored as UTC) are converted before matching.
"""

import datetime
import io
import re

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import (
    ParagraphProperties,
    Style,
    TableCellProperties,
    TableColumnProperties,
    TableProperties,
    TextProperties,
)
from odf.table import (
    CoveredTableCell,
    ContentValidation,
    ContentValidations,
    Table,
    TableCell,
    TableColumn,
    TableRow,
)
from odf.text import P
from sqlmodel import select

from shared_planner import tz
from shared_planner.db.models import Reservation, Shop, TimeSlot, User
from shared_planner.db.session import SessionLock

# Weekday names (Monday=0) used for the day labels.
WEEKDAYS_FR = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
]

# Export range modes.
RANGE_WEEK = "week"
RANGE_FORTNIGHT = "fortnight"
RANGE_ALL = "all"

# How many weeks each fixed-length range spans.
_FIXED_RANGE_WEEKS = {RANGE_WEEK: 1, RANGE_FORTNIGHT: 2}


def _local_monday(date: datetime.date) -> datetime.date:
    return date - datetime.timedelta(days=date.weekday())


def _build_styles(doc: OpenDocumentSpreadsheet) -> None:
    """Register all named cell/column styles used by the export."""

    def cell_style(name, *, bg=None, color=None, bold=False, size=None,
                   align=None, italic=False, border="0.5pt solid #b8c2cc"):
        style = Style(name=name, family="table-cell")
        style.addElement(TableCellProperties(border=border, **({"backgroundcolor": bg} if bg else {})))
        text_props = {}
        if color:
            text_props["color"] = color
        if bold:
            text_props["fontweight"] = "bold"
        if italic:
            text_props["fontstyle"] = "italic"
        if size:
            text_props["fontsize"] = size
        if text_props:
            style.addElement(TextProperties(**text_props))
        if align:
            style.addElement(ParagraphProperties(textalign=align))
        doc.automaticstyles.addElement(style)

    cell_style("Title", bg="#1f3a5f", color="#ffffff", bold=True, size="16pt", align="center", border="none")
    cell_style("Subtitle", color="#5a6b7b", italic=True, size="10pt", align="center", border="none")
    cell_style("WeekHeader", bg="#2e7d6b", color="#ffffff", bold=True, size="12pt", align="center")
    cell_style("ColHeader", bg="#d7e3ec", color="#1f3a5f", bold=True, align="center")
    cell_style("DayCell", bg="#eef3f7", color="#1f3a5f", bold=True, align="left")
    cell_style("TimeCell", bg="#f6f9fb", color="#33475b", align="center")
    cell_style("Filled", bg="#e3f4e1", color="#1e4620", align="center")
    cell_style("ToFill", bg="#fff7df", color="#9a7b14", italic=True, align="center")
    cell_style("NA", bg="#eceff1", color="#b0bec5", align="center")
    cell_style("ContactHeader", bg="#1f3a5f", color="#ffffff", bold=True, align="left")
    cell_style("Contact", align="left")

    # Column widths.
    for name, width in (("ColDay", "4.2cm"), ("ColTime", "3cm"), ("ColVol", "4cm"), ("ColEmail", "6cm")):
        style = Style(name=name, family="table-column")
        style.addElement(TableColumnProperties(columnwidth=width))
        doc.automaticstyles.addElement(style)

    # Make tables left-aligned with visible grid.
    table_style = Style(name="PlanningTable", family="table")
    table_style.addElement(TableProperties(**{"writingmode": "lr-tb"}))
    doc.automaticstyles.addElement(table_style)


def _text_cell(stylename: str, value: str = "", *, span: int = 1, validation: str | None = None):
    """Build a string table-cell, optionally spanning columns / with a validation."""
    kwargs = {"stylename": stylename, "valuetype": "string"}
    if span > 1:
        kwargs["numbercolumnsspanned"] = str(span)
        kwargs["numberrowsspanned"] = "1"
    if validation:
        kwargs["contentvalidationname"] = validation
    cell = TableCell(**kwargs)
    cell.addElement(P(text=value))
    return cell


def _add_row(table: Table, cells: list) -> None:
    row = TableRow()
    for cell in cells:
        row.addElement(cell)
    table.addElement(row)


def _spanned_row(table: Table, stylename: str, value: str, total_cols: int) -> None:
    """A single value spanning the whole width of the table."""
    cells = [_text_cell(stylename, value, span=total_cols)]
    cells += [CoveredTableCell() for _ in range(total_cols - 1)]
    _add_row(table, cells)


def _sanitize_sheet_name(name: str, used: set[str]) -> str:
    """ODF sheet names can't contain []*?:/\\ and must be unique & <=31 chars."""
    cleaned = re.sub(r"[\[\]\*\?:/\\']", " ", name).strip() or "Boutique"
    cleaned = cleaned[:31]
    candidate = cleaned
    i = 2
    while candidate.lower() in used:
        suffix = f" ({i})"
        candidate = cleaned[: 31 - len(suffix)] + suffix
        i += 1
    used.add(candidate.lower())
    return candidate


def _weeks_in_range(range_mode: str, last_reservation_end_local: datetime.datetime | None) -> list[datetime.date]:
    """Return the list of week-start (Monday) dates to render."""
    today_local = tz.utc_to_local(tz.now()).date()
    start_monday = _local_monday(today_local)

    if range_mode in _FIXED_RANGE_WEEKS:
        count = _FIXED_RANGE_WEEKS[range_mode]
    else:  # RANGE_ALL -> up to the week of the last reservation
        if last_reservation_end_local is None:
            count = 1
        else:
            last_monday = _local_monday(last_reservation_end_local.date())
            count = max(1, ((last_monday - start_monday).days // 7) + 1)

    return [start_monday + datetime.timedelta(weeks=w) for w in range(count)]


def _slot_volunteers(
    slot: TimeSlot, day_date: datetime.date, reservations: list[Reservation]
) -> tuple[list[str], int]:
    """Names booked into this slot on this date, and the number of places to show."""
    slot_start = tz.local_to_utc(datetime.datetime.combine(day_date, slot.start_time))
    slot_end = tz.local_to_utc(datetime.datetime.combine(day_date, slot.end_time))
    booked = [
        r for r in reservations if r.start_time < slot_end and r.end_time > slot_start
    ]
    names = sorted(r.user.full_name for r in booked)
    places = max(slot.max_volunteers, len(names))
    return names, places


def _hm(t: datetime.time) -> str:
    return t.strftime("%H:%M")


def _build_shop_sheet(
    doc: OpenDocumentSpreadsheet,
    shop: Shop,
    weeks: list[datetime.date],
    reservations: list[Reservation],
    contacts_validation: str,
    sheet_name: str,
) -> None:
    slots = list(shop.time_slots)
    max_vol = max((s.max_volunteers for s in slots), default=1)
    max_vol = max(max_vol, 1)
    # Account for any over-booked slot across the range so the grid is wide enough.
    for monday in weeks:
        for offset in range(7):
            day_date = monday + datetime.timedelta(days=offset)
            for slot in slots:
                if slot.day == day_date.weekday() and slot.valid_from <= day_date <= slot.valid_until:
                    _, places = _slot_volunteers(slot, day_date, reservations)
                    max_vol = max(max_vol, places)

    total_cols = 2 + max_vol  # day, time, volunteer columns

    table = Table(name=sheet_name, stylename="PlanningTable")
    table.addElement(TableColumn(stylename="ColDay"))
    table.addElement(TableColumn(stylename="ColTime"))
    table.addElement(TableColumn(stylename="ColVol", numbercolumnsrepeated=str(max_vol)))

    # Title + subtitle.
    _spanned_row(table, "Title", f"{shop.name} — Planning des bénévoles", total_cols)
    tzname = tz.get_server_tz().zone
    generated = tz.utc_to_local(tz.now()).strftime("%d/%m/%Y %H:%M")
    subtitle = f"{shop.location}  ·  généré le {generated} ({tzname})"
    _spanned_row(table, "Subtitle", subtitle, total_cols)
    _add_row(table, [TableCell() for _ in range(total_cols)])  # spacer

    for monday in weeks:
        sunday = monday + datetime.timedelta(days=6)
        # Collect the (day, slot) rows for this week.
        day_rows = []
        for offset in range(7):
            day_date = monday + datetime.timedelta(days=offset)
            day_slots = [
                s
                for s in slots
                if s.day == day_date.weekday() and s.valid_from <= day_date <= s.valid_until
            ]
            day_slots.sort(key=lambda s: s.start_time)
            for i, slot in enumerate(day_slots):
                day_rows.append((day_date, slot, i == 0))

        if not day_rows:
            continue

        _spanned_row(
            table,
            "WeekHeader",
            f"Semaine du {monday.strftime('%d/%m/%Y')} au {sunday.strftime('%d/%m/%Y')}",
            total_cols,
        )
        header_cells = [_text_cell("ColHeader", "Jour"), _text_cell("ColHeader", "Créneau")]
        header_cells += [_text_cell("ColHeader", f"Bénévole {n + 1}") for n in range(max_vol)]
        _add_row(table, header_cells)

        for day_date, slot, is_first in day_rows:
            day_label = f"{WEEKDAYS_FR[day_date.weekday()].capitalize()} {day_date.strftime('%d/%m')}" if is_first else ""
            names, places = _slot_volunteers(slot, day_date, reservations)
            cells = [
                _text_cell("DayCell", day_label),
                _text_cell("TimeCell", f"{_hm(slot.start_time)} – {_hm(slot.end_time)}"),
            ]
            for col in range(max_vol):
                if col < len(names):
                    cells.append(_text_cell("Filled", names[col]))
                elif col < places:
                    cells.append(_text_cell("ToFill", "", validation=contacts_validation))
                else:
                    cells.append(_text_cell("NA", ""))
            _add_row(table, cells)

        _add_row(table, [TableCell() for _ in range(total_cols)])  # spacer between weeks

    doc.spreadsheet.addElement(table)


def _build_contacts_sheet(doc: OpenDocumentSpreadsheet, users: list[User]) -> None:
    table = Table(name="Contacts")
    table.addElement(TableColumn(stylename="ColDay"))
    table.addElement(TableColumn(stylename="ColTime"))
    table.addElement(TableColumn(stylename="ColEmail"))
    table.addElement(TableColumn(stylename="ColTime"))

    header = [
        _text_cell("ContactHeader", "Nom"),
        _text_cell("ContactHeader", "Groupe"),
        _text_cell("ContactHeader", "Email"),
        _text_cell("ContactHeader", "Téléphone"),
    ]
    _add_row(table, header)
    for user in users:
        _add_row(
            table,
            [
                _text_cell("Contact", user.full_name),
                _text_cell("Contact", user.group or ""),
                _text_cell("Contact", user.email),
                _text_cell("Contact", user.phone or ""),
            ],
        )
    doc.spreadsheet.addElement(table)


def build_planning_ods(range_mode: str) -> bytes:
    """Build the planning workbook and return the ODS file bytes."""
    if range_mode not in (RANGE_WEEK, RANGE_FORTNIGHT, RANGE_ALL):
        range_mode = RANGE_WEEK

    doc = OpenDocumentSpreadsheet()
    _build_styles(doc)

    with SessionLock() as session:
        shops = list(session.exec(select(Shop).order_by(Shop.name)))
        users = list(session.exec(select(User).order_by(User.full_name)))
        all_reservations = list(session.exec(select(Reservation)))

        # Determine the export range from the last reservation (local time).
        last_end_local = None
        if all_reservations:
            last_end_local = tz.utc_to_local(max(r.end_time for r in all_reservations))
        weeks = _weeks_in_range(range_mode, last_end_local)

        # One content validation referencing the contacts name column (A2:A{n+1}).
        last_contact_row = len(users) + 1
        validation_name = "contacts_list"
        validation = ContentValidation(
            name=validation_name,
            condition=f"of:cell-content-is-in-list([$Contacts.$A$2:$A${last_contact_row}])",
            allowemptycell="true",
            displaylist="unsorted",
        )
        validations = ContentValidations()
        validations.addElement(validation)
        doc.spreadsheet.addElement(validations)

        used_names: set[str] = set()
        for shop in shops:
            shop_reservations = [r for r in all_reservations if r.shop_id == shop.id]
            sheet_name = _sanitize_sheet_name(shop.name, used_names)
            _build_shop_sheet(
                doc, shop, weeks, shop_reservations, validation_name, sheet_name
            )

        _build_contacts_sheet(doc, users)

    buffer = io.BytesIO()
    doc.write(buffer)
    return buffer.getvalue()
