import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from shared_planner.api.auth import CurrentAdmin
from shared_planner.db.models import Notification, TimeSlot, Shop
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
        # Reservations are pinned to the slot's day/times at booking. Moving the
        # slot (or shrinking its validity) under upcoming bookings would detach
        # them from the planning while they'd still show in the volunteers' own
        # lists, so refuse and let the admin handle those bookings first.
        moved = (
            slot.day != existing.day
            or slot.start_time != existing.start_time
            or slot.end_time != existing.end_time
        )
        for res in existing.booked_by:
            if res.end_time <= tz.now():
                continue
            res_date = tz.utc_to_local(res.start_time).date()
            if moved or not (slot.valid_from <= res_date <= slot.valid_until):
                raise HTTPException(
                    status_code=400, detail="error.slot.has_reservations"
                )
        existing.day = slot.day
        existing.start_time = slot.start_time
        existing.end_time = slot.end_time
        existing.max_volunteers = slot.max_volunteers
        existing.valid_from = slot.valid_from
        existing.valid_until = slot.valid_until
        session.add(existing)
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
        # Delete associated reservations first (no ORM cascade since FK is
        # nullable). Bookings are linked through ``booked_by``; ``reservations``
        # only covers the legacy ``time_slot_id`` FK. Leaving them behind would
        # orphan them: still listed for the volunteer, invisible in the planning.
        for res in {r.id: r for r in [*existing.reservations, *existing.booked_by]}.values():
            # Volunteers didn't ask for this, so always mail them (like a
            # reassignment), regardless of the self-cancel email setting.
            if res.end_time > tz.now():
                session.add(
                    Notification.create(
                        res.user,
                        "notification.reservation_cancelled",
                        {
                            "shop": res.shop.name,
                            "datetime-start_time": res.start_time.strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                            "duration": int(
                                (res.end_time - res.start_time).total_seconds() // 60
                            ),
                            "ics": res.ics_data(cancel=True),
                        },
                        route=f"/shops/{res.shop.id}/{monday_str(tz.utc_to_local(res.start_time))}",
                        mail=True,
                    )
                )
            session.delete(res)
        session.delete(existing)
        session.commit()
