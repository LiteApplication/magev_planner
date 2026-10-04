import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from shared_planner.api.auth import CurrentAdmin
from shared_planner.db.models import Notification, Reservation, TimeSlot, Shop
from shared_planner.db.session import SessionLock
from shared_planner.week import monday_str
from shared_planner import tz

router = APIRouter(prefix="/slots", tags=["slots"])


class TimeSlotIn(BaseModel):
    day: int
    start_time: datetime.time
    end_time: datetime.time
    max_volunteers: int
    valid_from: datetime.date
    valid_until: datetime.date


def _check_slot_values(slot: TimeSlotIn) -> None:
    if not 0 <= slot.day <= 6:
        raise HTTPException(status_code=400, detail="error.slot.invalid_day")
    if slot.max_volunteers < 1:
        raise HTTPException(status_code=400, detail="error.slot.invalid_max_volunteers")


class TimeSlotOut(BaseModel):
    id: int
    shop_id: int
    day: int
    start_time: datetime.time
    end_time: datetime.time
    max_volunteers: int
    valid_from: datetime.date
    valid_until: datetime.date

    @classmethod
    def from_slot(cls, slot: TimeSlot) -> "TimeSlotOut":
        return cls(
            id=slot.id,
            shop_id=slot.shop_id,
            day=slot.day,
            start_time=slot.start_time,
            end_time=slot.end_time,
            max_volunteers=slot.max_volunteers,
            valid_from=slot.valid_from,
            valid_until=slot.valid_until,
        )


@router.get("/{shop_id}/list")
def list_slots(shop_id: int) -> list[TimeSlotOut]:
    with SessionLock() as session:
        shop = session.get(Shop, shop_id)
        if shop is None:
            raise HTTPException(status_code=404, detail="error.shop.not_found")
        result = [TimeSlotOut.from_slot(s) for s in shop.time_slots]
    return result


@router.post("/{shop_id}/create", dependencies=[Depends(CurrentAdmin)])
def create_slot(shop_id: int, slot: TimeSlotIn) -> TimeSlotOut:
    with SessionLock() as session:
        shop = session.get(Shop, shop_id)
        if shop is None:
            raise HTTPException(status_code=404, detail="error.shop.not_found")
        if slot.start_time >= slot.end_time:
            raise HTTPException(status_code=400, detail="error.slot.invalid_time")
        if slot.valid_from > slot.valid_until:
            raise HTTPException(status_code=400, detail="error.slot.invalid_dates")
        _check_slot_values(slot)
        new_slot = TimeSlot(
            shop_id=shop_id,
            day=slot.day,
            start_time=slot.start_time,
            end_time=slot.end_time,
            max_volunteers=slot.max_volunteers,
            valid_from=slot.valid_from,
            valid_until=slot.valid_until,
        )
        session.add(new_slot)
        session.commit()
        session.refresh(new_slot)
        result = TimeSlotOut.from_slot(new_slot)
    return result


def _notification_data(res: Reservation, cancel: bool = False, update: bool = False) -> dict:
    return {
        "shop": res.shop.name,
        "maps_link": res.shop.maps_link,
        "datetime-start_time": res.start_time.strftime("%Y-%m-%d %H:%M"),
        "duration": int((res.end_time - res.start_time).total_seconds() // 60),
        "ics": res.ics_data(cancel=cancel, update=update),
    }


def _route(res: Reservation) -> str:
    return f"/shops/{res.shop.id}/{monday_str(tz.utc_to_local(res.start_time))}"


def _reschedule(
    session, res: Reservation, slot: TimeSlot, new_date: datetime.date | None
) -> None:
    """Re-derive ``res`` after an admin changed (or deleted) one of its slots.

    ``slot`` already holds its new definition; ``new_date`` is the local date it
    now falls on for this booking, or ``None`` when the booking loses it (slot
    deleted, or the new validity excludes that date). The reservation is rebuilt
    from its remaining slots: it keeps the first contiguous run, any further run
    (a merged booking split by the change) becomes its own reservation, and it's
    deleted when no slot is left. The volunteer didn't ask for any of this, so
    they're always mailed, regardless of the self-service email settings.
    """
    res_date = tz.utc_to_local(res.start_time).date()
    prev_start, prev_end = res.start_time, res.end_time

    dated = [(res_date, s) for s in res.booked_slots if s.id != slot.id]
    if new_date is not None:
        dated.append((new_date, slot))
    dated.sort(key=lambda d: (d[0], d[1].start_time))

    runs: list[tuple[datetime.date, list[TimeSlot]]] = []
    for date, s in dated:
        if runs and runs[-1][0] == date and runs[-1][1][-1].end_time == s.start_time:
            runs[-1][1].append(s)
        else:
            runs.append((date, [s]))

    if not runs:
        session.add(
            Notification.create(
                res.user,
                "notification.reservation_cancelled",
                _notification_data(res, cancel=True),
                route=_route(res),
                mail=True,
            )
        )
        session.delete(res)
        return

    def span(date: datetime.date, run: list[TimeSlot]):
        return (
            tz.local_to_utc(datetime.datetime.combine(date, run[0].start_time)),
            tz.local_to_utc(datetime.datetime.combine(date, run[-1].end_time)),
        )

    (date, run), *others = runs
    res.start_time, res.end_time = span(date, run)
    res.booked_slots = run
    res.time_slot_id = None
    session.add(res)
    if (res.start_time, res.end_time) != (prev_start, prev_end):
        data = _notification_data(res, update=True)
        data["datetime-previous_start_time"] = prev_start.strftime("%Y-%m-%d %H:%M")
        data["previous_duration"] = int((prev_end - prev_start).total_seconds() // 60)
        session.add(
            Notification.create(
                res.user,
                "notification.reservation_modified",
                data,
                route=_route(res),
                mail=True,
            )
        )

    for date, run in others:
        start, end = span(date, run)
        split = Reservation(
            user_id=res.user_id,
            shop_id=res.shop_id,
            start_time=start,
            end_time=end,
            validated=res.validated,
            booked_slots=run,
        )
        session.add(split)
        session.flush()
        session.add(
            Notification.create(
                res.user,
                "notification.reservation_created",
                _notification_data(split),
                route=_route(split),
                mail=True,
            )
        )


@router.put("/{slot_id}/update", dependencies=[Depends(CurrentAdmin)])
def update_slot(slot_id: int, slot: TimeSlotIn) -> TimeSlotOut:
    with SessionLock() as session:
        existing = session.get(TimeSlot, slot_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="error.slot.not_found")
        if slot.start_time >= slot.end_time:
            raise HTTPException(status_code=400, detail="error.slot.invalid_time")
        if slot.valid_from > slot.valid_until:
            raise HTTPException(status_code=400, detail="error.slot.invalid_dates")
        _check_slot_values(slot)
        day_shift = datetime.timedelta(days=slot.day - existing.day)
        upcoming = [r for r in existing.booked_by if r.end_time > tz.now()]
        existing.day = slot.day
        existing.start_time = slot.start_time
        existing.end_time = slot.end_time
        existing.max_volunteers = slot.max_volunteers
        existing.valid_from = slot.valid_from
        existing.valid_until = slot.valid_until
        session.add(existing)
        # Upcoming bookings follow the slot (same week when its day changes);
        # those the new validity no longer covers are cancelled.
        for res in upcoming:
            new_date = tz.utc_to_local(res.start_time).date() + day_shift
            if not (slot.valid_from <= new_date <= slot.valid_until):
                new_date = None
            _reschedule(session, res, existing, new_date)
        session.commit()
        session.refresh(existing)
        result = TimeSlotOut.from_slot(existing)
    return result


@router.delete("/{slot_id}/delete", dependencies=[Depends(CurrentAdmin)])
def delete_slot(slot_id: int) -> None:
    with SessionLock() as session:
        existing = session.get(TimeSlot, slot_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="error.slot.not_found")
        # Upcoming bookings lose this slot (and are cancelled if it was their
        # only one); past ones go with it. ``reservations`` only covers the
        # legacy ``time_slot_id`` FK (no ORM cascade since it's nullable).
        handled = set()
        for res in list(existing.booked_by):
            handled.add(res.id)
            if res.end_time > tz.now():
                _reschedule(session, res, existing, None)
            else:
                session.delete(res)
        for res in list(existing.reservations):
            if res.id not in handled:
                session.delete(res)
        session.delete(existing)
        session.commit()
