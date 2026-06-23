"""Timezone helpers.

All datetimes are stored in the database as naive UTC. User-facing rendering on
the backend (emails, ICS files) converts to the configured ``server_timezone``
setting. The frontend converts UTC to the viewer's local time on its side.
"""

import datetime

import pytz


def get_server_tz() -> pytz.BaseTzInfo:
    """Return the configured server timezone, falling back to UTC."""
    from shared_planner.db.settings import get  # local import to avoid cycle

    try:
        return pytz.timezone(get("server_timezone").value)
    except Exception:
        return pytz.utc


def now() -> datetime.datetime:
    """Current time as a naive UTC datetime (matches how datetimes are stored)."""
    return datetime.datetime.now(pytz.utc).replace(tzinfo=None)


def local_to_utc(dt: datetime.datetime) -> datetime.datetime:
    """Interpret a naive wall-clock datetime as server-local and return naive UTC."""
    return (
        get_server_tz()
        .localize(dt)
        .astimezone(pytz.utc)
        .replace(tzinfo=None)
    )


def utc_to_local(dt: datetime.datetime) -> datetime.datetime:
    """Convert a naive UTC datetime to a naive server-local wall-clock datetime."""
    return (
        pytz.utc.localize(dt)
        .astimezone(get_server_tz())
        .replace(tzinfo=None)
    )
