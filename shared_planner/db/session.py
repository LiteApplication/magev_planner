import datetime
import json
import os
from sqlmodel import SQLModel, create_engine, Session as _Session
from sqlalchemy import Engine
from shared_planner import tz
from shared_planner.db.models import (
    User,
    Shop,
    OpeningTime,
    TimeSlot,
    Reservation,
    Token,
    Notification,
)


from contextlib import contextmanager


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


def _run_migrations(engine: Engine) -> None:
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if "reservation" in tables:
        cols = [c["name"] for c in inspector.get_columns("reservation")]
        if "time_slot_id" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE reservation ADD COLUMN time_slot_id INTEGER REFERENCES timeslot(id)"))
                conn.commit()
    if "user" in tables:
        cols = [c["name"] for c in inspector.get_columns("user")]
        if "phone" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE user ADD COLUMN phone VARCHAR NOT NULL DEFAULT ''"))
                conn.commit()
        if "first_name" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE user ADD COLUMN first_name VARCHAR NOT NULL DEFAULT ''"))
                conn.execute(text("ALTER TABLE user ADD COLUMN last_name VARCHAR NOT NULL DEFAULT ''"))
                if "full_name" in cols:
                    # Split the legacy full name at the first space: everything
                    # before it becomes the first name, the rest the last name.
                    rows = conn.execute(text("SELECT id, full_name FROM user")).fetchall()
                    for row_id, full_name in rows:
                        first, _, last = (full_name or "").partition(" ")
                        conn.execute(
                            text("UPDATE user SET first_name = :f, last_name = :l WHERE id = :i"),
                            {"f": first, "l": last, "i": row_id},
                        )
                    conn.execute(text("ALTER TABLE user DROP COLUMN full_name"))
                conn.commit()


# Directory holding the SQLite database file. Defaults to the current working
# directory (so ``./database.db`` for local dev); set DATA_DIR to a mounted
# folder in production so the database lives on a persistent volume.
DATA_DIR = os.environ.get("DATA_DIR", ".")
DB_PATH = os.path.join(DATA_DIR, "database.db")


class EngineContainer(metaclass=Singleton):
    engine: Engine

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.engine = create_engine(
            f"sqlite:///{DB_PATH}", pool_timeout=10, max_overflow=50, pool_size=5
        )
        SQLModel.metadata.create_all(self.engine)
        _run_migrations(self.engine)


@contextmanager
def SessionLock():
    session = _Session(EngineContainer().engine)
    try:
        yield session
    finally:
        session.close()


def load_dummies():
    engine = EngineContainer().engine

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with open("dummy_data.json") as f:
        data = json.load(f)
    users = data["users"]
    for user in users:
        user["hashed_password"] = bytes(user["hashed_password"], "utf-8")
    shops = data["shops"]
    for shop in shops:
        shop["available_from"] = datetime.datetime.strptime(
            shop["available_from"], "%Y-%m-%d"
        )
        shop["available_until"] = datetime.datetime.strptime(
            shop["available_until"], "%Y-%m-%d"
        )
    opening_times = data["opening_times"]
    for opening_time in opening_times:
        opening_time["start_time"] = datetime.datetime.strptime(
            opening_time["start_time"], "%H:%M"
        ).time()

        opening_time["end_time"] = datetime.datetime.strptime(
            opening_time["end_time"], "%H:%M"
        ).time()
    # Recurring time slots. Each JSON entry lists the weekdays it applies to and
    # is expanded into one TimeSlot per day.
    time_slots = []
    for entry in data.get("time_slots", []):
        for day in entry["days"]:
            time_slots.append(
                TimeSlot(
                    shop_id=entry["shop_id"],
                    day=day,
                    start_time=datetime.datetime.strptime(
                        entry["start_time"], "%H:%M"
                    ).time(),
                    end_time=datetime.datetime.strptime(
                        entry["end_time"], "%H:%M"
                    ).time(),
                    max_volunteers=entry["max_volunteers"],
                    valid_from=datetime.datetime.strptime(
                        entry["valid_from"], "%Y-%m-%d"
                    ).date(),
                    valid_until=datetime.datetime.strptime(
                        entry["valid_until"], "%Y-%m-%d"
                    ).date(),
                )
            )
    # Reservations are defined relative to the current date: a `day_offset`
    # (in days from today) plus wall-clock `start_time`/`end_time` ("HH:MM").
    # The wall-clock times are interpreted as server-local and stored as UTC.
    today = tz.now().date()
    reservations = data["reservations"]
    for reservation in reservations:
        day = today + datetime.timedelta(days=reservation.pop("day_offset"))
        start_time = datetime.datetime.strptime(reservation["start_time"], "%H:%M").time()
        end_time = datetime.datetime.strptime(reservation["end_time"], "%H:%M").time()
        reservation["start_time"] = tz.local_to_utc(
            datetime.datetime.combine(day, start_time)
        )
        reservation["end_time"] = tz.local_to_utc(
            datetime.datetime.combine(day, end_time)
        )

    tokens = data["tokens"]
    for token in tokens:
        token["expires_at"] = datetime.datetime.strptime(
            token["expires_at"], "%Y-%m-%d %H:%M:%S"
        )

    with SessionLock() as session:
        print("Adding data")
        for user in users:
            u = User(**user)
            session.add(u)
            session.add(
                Notification.create(u, "notification.test", {"test": "test value"})
            )
            session.add(
                Notification.create(
                    u, "notification.test", {"test": "test reminder"}, is_reminder=True
                )
            )
        for shop in shops:
            session.add(Shop(**shop))
        for opening_time in opening_times:
            session.add(OpeningTime(**opening_time))
        for time_slot in time_slots:
            session.add(time_slot)
        for reservation in reservations:
            session.add(Reservation(**reservation))
        for token in tokens:
            session.add(Token(**token))

        print("Committing")

        session.commit()
