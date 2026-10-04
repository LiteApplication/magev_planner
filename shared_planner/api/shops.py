import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select

from shared_planner.api.auth import CurrentAdmin, CurrentToken
from shared_planner.db.models import OpeningTime, Shop
from shared_planner.db.session import SessionLock

router = APIRouter(prefix="/shops", tags=["shops"])
timerange_router = APIRouter(prefix="/timeranges", tags=["timeranges"])


class ShopWithoutTimeRanges(BaseModel):
    """Data model for shop without time ranges."""

    id: int | None = None
    name: str
    description: str
    location: str
    maps_link: str
    min_time: int
    max_time: int
    available_from: datetime.date
    available_until: datetime.date

    @classmethod
    def from_shop(cls, shop: Shop):
        return cls(
            **shop.model_dump(
                include=[
                    "id",
                    "name",
                    "description",
                    "location",
                    "maps_link",
                    "min_time",
                    "max_time",
                    "available_from",
                    "available_until",
                ]
            ),
        )


class ShopWithTimeRanges(ShopWithoutTimeRanges):
    """Data model for shop with time ranges."""

    open_ranges: list["TimeRange"] = []

    @classmethod
    def from_shop(cls, shop: Shop):
        result = super().from_shop(shop)
        result.open_ranges = [
            TimeRange(
                **time_range.model_dump(
                    include=[
                        "id",
                        "day",
                        "start_time",
                        "end_time",
                    ]
                )
            )
            for time_range in shop.open_ranges
        ]
        return result


class TimeRange(BaseModel):
    """Data model for time range"""

    id: int | None = None
    day: int
    start_time: datetime.time
    end_time: datetime.time


def _check_time_range(
    new: TimeRange, existing: list[OpeningTime], exclude_id: int | None = None
) -> None:
    """Validate day and bounds, and that ``new`` overlaps no other range that day."""
    if not 0 <= new.day <= 6:
        raise HTTPException(status_code=400, detail="error.shop.invalid_day")
    if new.start_time >= new.end_time:
        raise HTTPException(status_code=400, detail="error.shop.negative_time_range")
    for ex in existing:
        if ex.id == exclude_id or ex.day != new.day:
            continue
        if ex.start_time < new.end_time and new.start_time < ex.end_time:
            raise HTTPException(status_code=400, detail="error.shop.time_range_overlap")


@router.get("/{shop_id}/get", dependencies=[Depends(CurrentToken)])
def get_shop(shop_id: int) -> ShopWithTimeRanges:
    """Get a specific shop"""
    with SessionLock() as session:
        shop = session.get(Shop, shop_id)
        if shop is None:
            raise HTTPException(status_code=404, detail="error.shop.not_found")

        result = ShopWithTimeRanges.from_shop(shop)
    return result


@router.get("/list", dependencies=[Depends(CurrentToken)])
def list_shops() -> list[ShopWithoutTimeRanges]:
    """List all shops"""
    with SessionLock() as session:
        statement = select(Shop)
        shops = session.exec(statement).all()
    return shops


@router.post("/create", dependencies=[Depends(CurrentAdmin)])
def create_shop(shop_data: ShopWithoutTimeRanges) -> Shop:
    """Create a new shop"""
    with SessionLock() as session:
        new_shop = Shop(**shop_data.model_dump())
        new_shop.id = None
        session.add(new_shop)
        session.commit()
        session.refresh(new_shop)
        result = ShopWithTimeRanges.from_shop(new_shop)
    return result


@router.delete("/{shop_id}/delete", dependencies=[Depends(CurrentAdmin)])
def delete_shop(shop_id: int) -> None:
    """Delete a specific shop"""
    with SessionLock() as session:
        shop = session.get(Shop, shop_id)
        if shop is None:
            raise HTTPException(status_code=404, detail="error.shop.not_found")
        session.delete(shop)
        session.commit()
    return None


@router.put("/update", dependencies=[Depends(CurrentAdmin)])
def update_shop(shop_data: ShopWithoutTimeRanges) -> ShopWithTimeRanges:
    """Update a specific shop"""
    with SessionLock() as session:
        if shop_data.id is None:
            raise HTTPException(status_code=400, detail="error.shop.no_id")

        shop = session.get(Shop, shop_data.id)
        if shop is None:
            raise HTTPException(status_code=404, detail="error.shop.not_found")

        # Update shop attributes
        for key, value in shop_data.model_dump().items():
            setattr(shop, key, value)
            session.add(shop)
        session.commit()
        session.refresh(shop)
        result = ShopWithTimeRanges.from_shop(shop)
    return result


@timerange_router.post("/{shop_id}/create", dependencies=[Depends(CurrentAdmin)])
def create_time_range(shop_id: int, time_range: TimeRange) -> ShopWithTimeRanges:
    """Create a new time range for a shop"""
    with SessionLock() as session:
        shop = session.get(Shop, shop_id)
        if shop is None:
            raise HTTPException(status_code=404, detail="error.shop.not_found")

        time_range.id = None

        _check_time_range(time_range, shop.open_ranges)

        new_time_range = OpeningTime(shop_id=shop.id, **time_range.model_dump())
        session.add(new_time_range)
        session.commit()
        session.refresh(new_time_range)
        session.refresh(shop)

        result = ShopWithTimeRanges.from_shop(shop)
    return result


@timerange_router.delete(
    "/{time_range_id}/delete", dependencies=[Depends(CurrentAdmin)]
)
def delete_time_range(time_range_id: int) -> None:
    """Delete a specific time range"""
    with SessionLock() as session:
        time_range = session.get(OpeningTime, time_range_id)
        if time_range is None:
            raise HTTPException(
                status_code=404, detail="error.shop.time_range_not_found"
            )
        session.delete(time_range)
        session.commit()
    return None


@timerange_router.put("/{time_range_id}/update", dependencies=[Depends(CurrentAdmin)])
def update_time_range(time_range_id: int, new_tr: TimeRange) -> ShopWithTimeRanges:
    """Update a specific time range"""
    with SessionLock() as session:
        time_range = session.get(OpeningTime, time_range_id)
        if time_range is None:
            raise HTTPException(
                status_code=404, detail="error.shop.time_range_not_found"
            )

        _check_time_range(new_tr, time_range.shop.open_ranges, exclude_id=time_range.id)

        time_range.day = new_tr.day
        time_range.start_time = new_tr.start_time
        time_range.end_time = new_tr.end_time

        session.add(time_range)
        session.commit()
        session.refresh(time_range)

        result = ShopWithTimeRanges.from_shop(time_range.shop)
    return result
