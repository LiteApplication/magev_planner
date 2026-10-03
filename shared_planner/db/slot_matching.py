import datetime

import pytz

from shared_planner.db.models import Reservation, TimeSlot
from shared_planner import tz


def matching_slots(
    reservation: Reservation,
    slots_by_shop: dict[int, list[TimeSlot]],
    server_tz: pytz.BaseTzInfo | None = None,
) -> list[TimeSlot]:
    """TimeSlot definitions that ``reservation``'s time range was booked against.

    A slot matches when its day-of-week/validity fits the reservation's local
    date and its time range sits fully inside the reservation's (a merged,
    multi-slot booking run covers several slots at once). Used to backfill or
    reconstruct the reservation<->slot link for reservations created without
    going through the normal booking endpoints (e.g. dummy data, migrations).

    Pass ``server_tz`` explicitly when the settings table can't be read through
    ``SessionLock`` (i.e. inside a migration, while the engine is still being
    built): ``tz.get_server_tz`` would otherwise silently fall back to UTC.
    """
    if server_tz is None:
        server_tz = tz.get_server_tz()

    def to_local(dt: datetime.datetime) -> datetime.datetime:
        return pytz.utc.localize(dt).astimezone(server_tz).replace(tzinfo=None)

    local_start = to_local(reservation.start_time)
    local_end = to_local(reservation.end_time)
    matches = []
    for slot in slots_by_shop.get(reservation.shop_id, []):
        if slot.day != local_start.weekday():
            continue
        if not (slot.valid_from <= local_start.date() <= slot.valid_until):
            continue
        slot_start = datetime.datetime.combine(local_start.date(), slot.start_time)
        slot_end = datetime.datetime.combine(local_start.date(), slot.end_time)
        if slot_start >= local_start and slot_end <= local_end:
            matches.append(slot)
    return matches
