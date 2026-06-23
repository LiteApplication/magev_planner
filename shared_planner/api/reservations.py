import datetime

from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import select

from shared_planner.api.auth import CurrentAdmin, CurrentUser, CurrentToken
from shared_planner.api.shops import ShopWithoutTimeRanges
from shared_planner.api.slots import TimeSlotOut
from shared_planner.db.models import Reservation, Shop, TimeSlot, User, Token, Notification
from shared_planner.db.session import SessionLock
from shared_planner.db.settings import get
from shared_planner.week import monday_str
from shared_planner import tz

router = APIRouter(prefix="/res", tags=["reservations"])


class ReservedTimeRange(BaseModel):
    """Data model for time range

    status :
    -1 = someone booked
    -2 = user booked

    if status => 0 then status is the user id of the person who booked.


    """

    id: int | None = None
    start_time: datetime.datetime
    duration_minutes: int
    status: int
    validated: bool = False
    title: str = ""
    shop: Shop | None = None

    @classmethod
    def from_reservation(
        cls, reservation: Reservation, user: User | None
    ) -> "ReservedTimeRange":
        if user is not None and reservation.user_id == user.id:
            status = -2
            title = "message.reservation.booked_by_you"
        elif user is None or user.admin:
            status = reservation.user_id
            title = f"{reservation.user.full_name} ({reservation.user.group})"
        else:
            status = -1
            title = "message.reservation.booked"

        return cls(
            id=reservation.id,
            start_time=reservation.start_time,
            duration_minutes=(
                reservation.end_time - reservation.start_time
            ).total_seconds()
            // 60,
            status=status,
            validated=reservation.validated,
            title=title,
            shop=ShopWithoutTimeRanges.from_shop(reservation.shop),
        )


class SlotStatus(BaseModel):
    """Status of a time slot for a specific date"""

    slot: TimeSlotOut
    date: datetime.date
    booked_count: int
    booked_by_me: bool
    reservation_id: int | None = None
    validated: bool = False


class BookSlotRequest(BaseModel):
    time_slot_id: int
    date: datetime.date


class BookMultipleSlotsRequest(BaseModel):
    time_slot_ids: list[int]
    date: datetime.date


@router.get("/{shop_id}/{monday}/list")
def get_planning(
    shop_id: int, monday: str, user: Annotated[User, Depends(CurrentUser)]
) -> list[list[SlotStatus]]:
    """Get the slot planning of a shop for a specific week"""
    with SessionLock() as session:
        shop = session.get(Shop, shop_id)
        if shop is None:
            raise HTTPException(status_code=404, detail="error.shop.not_found")

        week_start = datetime.datetime.strptime(monday, "%Y-%m-%d")
        if week_start.weekday() != 0:
            raise HTTPException(status_code=400, detail="error.reservation.not_monday")

        week_end = week_start + datetime.timedelta(days=7)
        # Fetch all reservations for this shop in this week. Reservations are stored
        # in UTC, so convert the local week bounds before querying.
        week_reservations = session.exec(
            select(Reservation).where(
                Reservation.shop_id == shop_id,
                Reservation.start_time >= tz.local_to_utc(week_start),
                Reservation.start_time < tz.local_to_utc(week_end),
            )
        ).all()

        result = []
        for day_offset in range(7):
            day_date = (week_start + datetime.timedelta(days=day_offset)).date()
            weekday = day_date.weekday()

            day_slots = [
                s
                for s in shop.time_slots
                if s.day == weekday and s.valid_from <= day_date <= s.valid_until
            ]
            day_slots.sort(key=lambda s: s.start_time)

            day_statuses = []
            for slot in day_slots:
                # Find reservations that overlap with this slot (compare in UTC)
                slot_start = tz.local_to_utc(
                    datetime.datetime.combine(day_date, slot.start_time)
                )
                slot_end = tz.local_to_utc(
                    datetime.datetime.combine(day_date, slot.end_time)
                )

                slot_reservations = [
                    r
                    for r in week_reservations
                    if (r.start_time < slot_end and r.end_time > slot_start)
                ]

                booked_count = len(slot_reservations)
                my_res = next(
                    (r for r in slot_reservations if r.user_id == user.id), None
                )

                day_statuses.append(
                    SlotStatus(
                        slot=TimeSlotOut.from_slot(slot),
                        date=day_date,
                        booked_count=booked_count,
                        booked_by_me=my_res is not None,
                        reservation_id=my_res.id if my_res else None,
                        validated=my_res.validated if my_res else False,
                    )
                )

            result.append(day_statuses)
        session.close()

    return result


@router.post("/{shop_id}/book")
def book_slot(
    shop_id: int,
    req: BookSlotRequest,
    user: Annotated[User, Depends(CurrentUser)],
) -> ReservedTimeRange:
    """Book a predefined time slot"""
    return book_slots(
        shop_id, BookMultipleSlotsRequest(time_slot_ids=[req.time_slot_id], date=req.date), user
    )


@router.post("/{shop_id}/book_multiple")
def book_slots(
    shop_id: int,
    req: BookMultipleSlotsRequest,
    user: Annotated[User, Depends(CurrentUser)],
) -> ReservedTimeRange:
    """Book multiple contiguous time slots as one reservation"""
    with SessionLock() as session:
        shop = session.get(Shop, shop_id)
        if shop is None:
            raise HTTPException(status_code=404, detail="error.shop.not_found")

        if not req.time_slot_ids:
            raise HTTPException(status_code=400, detail="error.reservation.no_slots")

        slots = []
        for slot_id in req.time_slot_ids:
            slot = session.get(TimeSlot, slot_id)
            if slot is None or slot.shop_id != shop_id:
                raise HTTPException(status_code=404, detail="error.slot.not_found")
            if not (slot.valid_from <= req.date <= slot.valid_until):
                raise HTTPException(status_code=400, detail="error.slot.not_active")
            if req.date.weekday() != slot.day:
                raise HTTPException(status_code=400, detail="error.slot.wrong_day")
            slots.append(slot)

        # Sort slots by time to determine overall range
        slots.sort(key=lambda s: s.start_time)

        if req.date < tz.utc_to_local(tz.now()).date() and not user.admin:
            raise HTTPException(status_code=400, detail="error.reservation.past_time")

        if req.date < shop.available_from.date() and not user.admin:
            raise HTTPException(status_code=400, detail="error.reservation.before_open")

        if req.date > shop.available_until.date() and not user.admin:
            raise HTTPException(status_code=400, detail="error.reservation.after_close")

        # Verification for each slot (reservations are stored in UTC)
        for slot in slots:
            slot_start = tz.local_to_utc(
                datetime.datetime.combine(req.date, slot.start_time)
            )
            slot_end = tz.local_to_utc(
                datetime.datetime.combine(req.date, slot.end_time)
            )

            # Use overlap check for existing reservations
            query = select(Reservation).where(
                Reservation.shop_id == shop_id,
                Reservation.start_time < slot_end,
                Reservation.end_time > slot_start,
            )
            existing = session.exec(query).all()

            if any(r.user_id == user.id for r in existing):
                raise HTTPException(
                    status_code=400, detail="error.reservation.already_booked"
                )

            if len(existing) >= slot.max_volunteers and not user.admin:
                raise HTTPException(status_code=400, detail="error.reservation.overlap")

        overall_start = tz.local_to_utc(
            datetime.datetime.combine(req.date, slots[0].start_time)
        )
        overall_end = tz.local_to_utc(
            datetime.datetime.combine(req.date, slots[-1].end_time)
        )

        new_reservation = Reservation(
            user_id=user.id,
            shop=shop,
            start_time=overall_start,
            end_time=overall_end,
            time_slot_id=None,
        )

        session.add(
            Notification.create(
                user,
                "notification.reservation_created",
                {
                    "shop": shop.name,
                    "datetime-start_time": overall_start.strftime("%Y-%m-%d %H:%M"),
                    "duration": int(
                        (overall_end - overall_start).total_seconds() // 60
                    ),
                    "ics": new_reservation.ics_data(),
                },
                route=f"/shops/{shop.id}/{monday_str(tz.utc_to_local(overall_start))}",
                mail=get("email_reservation_created").asBool()
                and (
                    tz.now()
                    < (
                        overall_start
                        - datetime.timedelta(
                            hours=get("email_notification_before").asInt()
                        )
                    )
                ),
            )
        )

        if get("notif_admin_reservation_created").asBool() and (
            get("notify_for_admin_actions").asBool() or not user.admin
        ):
            session.add(
                Notification.create(
                    None,
                    "notification.admin.reservation_created",
                    {
                        "user": user.full_name,
                        "shop": shop.name,
                        "datetime-start_time": overall_start.strftime("%Y-%m-%d %H:%M"),
                        "duration": int(
                            (overall_end - overall_start).total_seconds() // 60
                        ),
                    },
                    route=f"/shops/{shop.id}/{monday_str(tz.utc_to_local(overall_start))}",
                    is_reminder=True,
                    mail=get("email_admin_reservation_created").asBool(),
                )
            )

        session.add(new_reservation)
        session.commit()
        session.refresh(new_reservation)

        result = ReservedTimeRange.from_reservation(new_reservation, user)
    return result


@router.delete("/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int, user: Annotated[User, Depends(CurrentUser)]
) -> None:
    """Cancel a reservation"""
    with SessionLock() as session:
        reservation = session.get(Reservation, reservation_id)
        if reservation is None:
            raise HTTPException(status_code=404, detail="error.reservation.not_found")
        if reservation.user_id != user.id and not user.admin:
            raise HTTPException(status_code=403, detail="error.reservation.cant_cancel")
        if reservation.validated and not user.admin:
            raise HTTPException(
                status_code=400, detail="error.reservation.cant_cancel_validated"
            )

        session.add(
            Notification.create(
                reservation.user,
                "notification.reservation_cancelled",
                {
                    "shop": reservation.shop.name,
                    "datetime-start_time": reservation.start_time.strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "duration": int(
                        (reservation.end_time - reservation.start_time).total_seconds()
                        // 60
                    ),
                    "ics": reservation.ics_data(cancel=True),
                },
                route=f"/shops/{reservation.shop.id}/{monday_str(tz.utc_to_local(reservation.start_time))}",
                mail=get("email_reservation_cancelled").asBool(),
            )
        )

        if get("notif_admin_reservation_cancelled").asBool() and (
            get("notify_for_admin_actions").asBool() or not user.admin
        ):
            session.add(
                Notification.create(
                    None,
                    "notification.admin.reservation_cancelled",
                    {
                        "user": user.full_name,
                        "shop": reservation.shop.name,
                        "datetime-start_time": reservation.start_time.strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "duration": int(
                            (reservation.end_time - reservation.start_time).total_seconds()
                            // 60
                        ),
                    },
                    route=f"/shops/{reservation.shop.id}/{monday_str(tz.utc_to_local(reservation.start_time))}",
                    mail=get("email_admin_reservation_cancelled").asBool(),
                )
            )
        session.delete(reservation)
        session.commit()
    return None


@router.put("/{reservation_id}/validate", dependencies=[Depends(CurrentAdmin)])
def validate_reservation(reservation_id: int) -> ReservedTimeRange:
    """Validate a reservation"""
    with SessionLock() as session:
        reservation = session.get(Reservation, reservation_id)
        if reservation is None:
            raise HTTPException(status_code=404, detail="error.reservation.not_found")
        reservation.validated = True
        session.add(reservation)
        session.commit()
        session.refresh(reservation)
        result = ReservedTimeRange.from_reservation(reservation, None)
    return result


@router.get("/list_self")
def get_user_reservations(
    token: Annotated[Token, Depends(CurrentToken)],
) -> list[ReservedTimeRange]:
    """Get the reservations of the current user"""
    with SessionLock() as session:
        user = session.get(User, token.user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="error.user.not_found")
        reservations = sorted(
            [
                ReservedTimeRange.from_reservation(res, user)
                for res in user.reservations
            ],
            key=lambda res: res.start_time,
        )
    return reservations


@router.get("/list_self_future")
def get_user_future_reservations(
    token: Annotated[Token, Depends(CurrentToken)],
) -> list[ReservedTimeRange]:
    """Get the future reservations of the current user"""
    with SessionLock() as session:
        user = session.get(User, token.user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="error.user.not_found")
        reservations = sorted(
            [
                ReservedTimeRange.from_reservation(res, user)
                for res in filter(
                    lambda res: res.end_time > tz.now(),
                    user.reservations,
                )
            ],
            key=lambda res: res.start_time,
        )
    return reservations


@router.post("/search", dependencies=[Depends(CurrentAdmin)])
def search(
    shop_id: int | None = Body(None),
    user_id: int | None = Body(None),
    monday: str | None = Body(None),
) -> list[ReservedTimeRange]:
    """Search reservations by shop, user, and/or week."""
    with SessionLock() as session:
        query = select(Reservation)
        if shop_id is not None:
            query = query.where(Reservation.shop_id == shop_id)
        if user_id is not None:
            query = query.where(Reservation.user_id == user_id)
        if monday is not None:
            week_start = datetime.datetime.strptime(monday, "%Y-%m-%d")
            week_end = week_start + datetime.timedelta(days=7)
            query = query.where(
                Reservation.start_time >= tz.local_to_utc(week_start),
                Reservation.start_time < tz.local_to_utc(week_end),
            )
        reservations = session.exec(query)
        result = [ReservedTimeRange.from_reservation(res, None) for res in reservations]
    return result


@router.put("/{reservation_id}/reassign", dependencies=[Depends(CurrentAdmin)])
def reassign_reservation(
    reservation_id: int,
    user_id: int = Body(...),
) -> ReservedTimeRange:
    """Reassign a reservation to a different user"""
    with SessionLock() as session:
        reservation = session.get(Reservation, reservation_id)
        if reservation is None:
            raise HTTPException(status_code=404, detail="error.reservation.not_found")
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="error.user.not_found")
        reservation.user_id = user.id
        session.add(reservation)
        session.commit()
        session.refresh(reservation)

        session.add(
            Notification.create(
                user=reservation.user,
                message="notification.reservation_reassigned_old",
                data={
                    "shop": reservation.shop.name,
                    "datetime-start_time": reservation.start_time.strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "duration": int(
                        (reservation.end_time - reservation.start_time).total_seconds()
                        // 60
                    ),
                    "ics": reservation.ics_data(cancel=True),
                },
                mail=True,
            )
        )
        session.add(
            Notification.create(
                user=user,
                message="notification.reservation_reassigned_new",
                data={
                    "shop": reservation.shop.name,
                    "datetime-start_time": reservation.start_time.strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "duration": int(
                        (reservation.end_time - reservation.start_time).total_seconds()
                        // 60
                    ),
                    "ics": reservation.ics_data(),
                },
                route=f"/shops/{reservation.shop.id}/{monday_str(tz.utc_to_local(reservation.start_time))}",
                mail=True,
            )
        )
        session.commit()

        result = ReservedTimeRange.from_reservation(reservation, user)
    return result


@router.get("/all_data/{api_key}")
def get_all_data(api_key: str) -> str:
    """Export all reservations as CSV"""
    if get("api_key").value == "":
        raise HTTPException(status_code=403, detail="error.api_key_not_set")
    if api_key != get("api_key").value:
        raise HTTPException(status_code=403, detail="error.api_key_invalid")

    import csv
    from io import StringIO

    output = StringIO()

    with SessionLock() as session:
        query = (
            select(Reservation)
            .order_by(Reservation.start_time)
            .order_by(Reservation.shop_id)
        )
        reservations = session.exec(query)
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "shop_name",
                "user_name",
                "user_email",
                "user_group",
                "user_admin",
                "start_time",
                "duration",
            ],
        )
        writer.writeheader()
        for res in reservations:
            writer.writerow(
                {
                    "shop_name": res.shop.name,
                    "user_name": res.user.full_name,
                    "user_email": res.user.email,
                    "user_group": res.user.group,
                    "user_admin": res.user.admin,
                    "start_time": res.start_time,
                    "duration": (res.end_time - res.start_time).total_seconds()
                    / (60 * 60),
                }
            )
    value = output.getvalue()
    output.close()
    response = StreamingResponse(content=iter([value]), media_type="text/csv")
    return response
