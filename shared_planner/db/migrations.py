"""Ordered, version-tracked SQLite schema migrations.

Each migration is a numbered, idempotent step applied against the raw
connection. ``run_migrations`` creates a ``schema_migrations`` table (if
missing) recording which versions have been applied, then runs every
migration whose version isn't recorded yet, in order, each in its own
transaction.

To add a migration: write a new ``_migrate_xxx`` function and append a new
``Migration(version, name, func)`` entry at the end of ``MIGRATIONS`` with
the next integer version. Never renumber, remove, or reorder existing
entries — the version is a permanent, applied-once marker, and a database
that already recorded version N must never see it run again.
"""

from dataclasses import dataclass
from typing import Callable

from sqlalchemy import Connection, Engine, inspect, text

from shared_planner import tz


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    apply: Callable[[Connection], None]


def _tables(conn: Connection) -> set[str]:
    return set(inspect(conn).get_table_names())


def _columns(conn: Connection, table: str) -> set[str]:
    return {c["name"] for c in inspect(conn).get_columns(table)}


def _migrate_mailtemplate_subject(conn: Connection) -> None:
    if "mailtemplate" not in _tables(conn):
        return
    if "subject" not in _columns(conn, "mailtemplate"):
        conn.execute(
            text("ALTER TABLE mailtemplate ADD COLUMN subject VARCHAR NOT NULL DEFAULT ''")
        )


def _migrate_reservation_time_slot_id(conn: Connection) -> None:
    if "reservation" not in _tables(conn):
        return
    if "time_slot_id" not in _columns(conn, "reservation"):
        conn.execute(
            text(
                "ALTER TABLE reservation ADD COLUMN time_slot_id INTEGER "
                "REFERENCES timeslot(id)"
            )
        )


def _migrate_user_phone(conn: Connection) -> None:
    if "user" not in _tables(conn):
        return
    if "phone" not in _columns(conn, "user"):
        conn.execute(
            text("ALTER TABLE user ADD COLUMN phone VARCHAR NOT NULL DEFAULT ''")
        )


def _migrate_user_split_full_name(conn: Connection) -> None:
    if "user" not in _tables(conn):
        return
    cols = _columns(conn, "user")
    if "first_name" not in cols:
        conn.execute(
            text("ALTER TABLE user ADD COLUMN first_name VARCHAR NOT NULL DEFAULT ''")
        )
        conn.execute(
            text("ALTER TABLE user ADD COLUMN last_name VARCHAR NOT NULL DEFAULT ''")
        )
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


def _migrate_passwordreset_created_at(conn: Connection) -> None:
    if "passwordreset" not in _tables(conn):
        return
    if "created_at" not in _columns(conn, "passwordreset"):
        conn.execute(
            text(
                "ALTER TABLE passwordreset ADD COLUMN created_at DATETIME "
                "NOT NULL DEFAULT '1970-01-01 00:00:00'"
            )
        )


# Historical migrations (1-4) were previously run unconditionally on every
# startup, guarded only by their own column-existence checks. They're
# reproduced here verbatim as the first entries so that databases which
# never had a ``schema_migrations`` table (i.e. every existing deployment)
# bootstrap cleanly: each still checks before altering, so replaying them
# against an already-migrated database is a no-op.
MIGRATIONS: list[Migration] = [
    Migration(1, "mailtemplate.subject", _migrate_mailtemplate_subject),
    Migration(2, "reservation.time_slot_id", _migrate_reservation_time_slot_id),
    Migration(3, "user.phone", _migrate_user_phone),
    Migration(4, "user.first_name/last_name (split full_name)", _migrate_user_split_full_name),
    Migration(5, "passwordreset.created_at", _migrate_passwordreset_created_at),
]


def _ensure_migrations_table(conn: Connection) -> None:
    conn.execute(
        text(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "version INTEGER PRIMARY KEY, "
            "name VARCHAR NOT NULL, "
            "applied_at DATETIME NOT NULL"
            ")"
        )
    )


def current_version(engine: Engine) -> int:
    """The highest migration version recorded as applied (0 if none)."""
    with engine.connect() as conn:
        _ensure_migrations_table(conn)
        conn.commit()
        return conn.execute(text("SELECT MAX(version) FROM schema_migrations")).scalar() or 0


def run_migrations(engine: Engine) -> None:
    with engine.connect() as conn:
        _ensure_migrations_table(conn)
        conn.commit()
        applied = {
            row[0]
            for row in conn.execute(text("SELECT version FROM schema_migrations")).fetchall()
        }

    for migration in sorted(MIGRATIONS, key=lambda m: m.version):
        if migration.version in applied:
            continue
        with engine.begin() as conn:
            migration.apply(conn)
            conn.execute(
                text(
                    "INSERT INTO schema_migrations (version, name, applied_at) "
                    "VALUES (:v, :n, :a)"
                ),
                {"v": migration.version, "n": migration.name, "a": tz.now()},
            )
