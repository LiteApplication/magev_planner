from datetime import datetime, timedelta, timezone
import pytz


def create_ics(
    event_name: str,
    start_time: str,  # yyyy-mm-dd hh:mm
    duration_minutes: int,
    description: str,
    location: str,
    organizer: str,  # "Name <email>"
    id: str,
    cancel: bool = False,
    update: bool = False,
) -> str:
    """Create an iCalendar file for an event"""

    # Parse the start time. Reservations are stored in UTC, so the incoming
    # string is already UTC.
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    start_time = pytz.utc.localize(start_time)
    # Round that to te nearest 15 minutes
    start_time = start_time + timedelta(minutes=7.5)
    start_time -= timedelta(
        minutes=start_time.minute % 15,
        seconds=start_time.second,
        microseconds=start_time.microsecond,
    )

    # Calculate the end time
    end_time = start_time + timedelta(minutes=duration_minutes)

    # Format the datetime objects to the iCalendar datetime format
    dt_format = "%Y%m%dT%H%M%SZ"
    description = description.replace("\n", "\\n")
    # Parse the organizer
    organizer_name, organizer_email = organizer.split("<")
    organizer_email = organizer_email[:-1]
    organizer_name = organizer_name.strip()
    organizer_email = organizer_email.strip().lower()

    # Sequence number
    sequence = 0
    if update:
        sequence = 1
    if cancel:
        sequence = 2

    # Create the iCalendar content
    method = "PUBLISH" if (not update and not cancel) else "REQUEST"
    status = "CANCELLED" if cancel else "CONFIRMED"
    start_time_str = start_time.strftime(dt_format)
    end_time_str = end_time.strftime(dt_format)
    now_str = datetime.now(timezone.utc).strftime(dt_format)

    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//LiteApp//SharedPlanner//EN
METHOD:{method}
X-WR-TIMEZONE:Europe/Paris
BEGIN:VTIMEZONE
TZID:Europe/Paris
BEGIN:STANDARD
DTSTART:20201025T030000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:20200329T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
END:DAYLIGHT
END:VTIMEZONE
BEGIN:VEVENT
UID:{id}@liteapp.fr
DTSTAMP:{now_str}
DTSTART:{start_time_str}
DTEND:{end_time_str}
SUMMARY:{event_name}
DESCRIPTION:{description}
LOCATION:{location}
ORGANIZER;CN={organizer_name}:MAILTO:{organizer_email}
STATUS:{status}
SEQUENCE:{sequence}
END:VEVENT
END:VCALENDAR"""
