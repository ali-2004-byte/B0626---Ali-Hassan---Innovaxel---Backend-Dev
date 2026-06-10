import sqlite3


def get_event_by_id(conn: sqlite3.Connection, event_id: int):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, total_seats, event_date
        FROM events
        WHERE id = ?
        """,
        (event_id,)
    )
    return cursor.fetchone()


def insert_event(conn: sqlite3.Connection, name: str, total_seats: int, event_date: str) -> int:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO events (name, total_seats, event_date)
        VALUES (?, ?, ?)
        """,
        (name, total_seats, event_date)
    )
    return cursor.lastrowid


def list_events(
    conn: sqlite3.Connection,
    upcoming_only: bool = False,
    sort_by_date: bool = False
):
    
    query = """
    SELECT
        e.id,
        e.name,
        e.event_date,
        e.total_seats,
        -- Seat availability is derived from active registrations
        -- rather than stored to avoid synchronization issues.
        COUNT(CASE WHEN r.status = 'active' THEN 1 END) AS total_registrations,
        e.total_seats - COUNT(CASE WHEN r.status = 'active' THEN 1 END) AS available_seats
    FROM events e
    LEFT JOIN registrations r ON r.event_id = e.id
    """

    conditions = []
    if upcoming_only:
        conditions.append("e.event_date > datetime('now')")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY e.id"

    if sort_by_date:
        query += " ORDER BY e.event_date ASC"

    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def count_active_registrations(conn: sqlite3.Connection, event_id: int) -> int:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM registrations
        WHERE event_id = ?
          AND status = 'active'
        """,
        (event_id,)
    )
    row = cursor.fetchone()
    return row["count"] if row else 0


def insert_registration(conn: sqlite3.Connection, event_id: int, user_name: str) -> int:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO registrations (event_id, user_name)
        VALUES (?, ?)
        """,
        (event_id, user_name)
    )
    return cursor.lastrowid


def get_registration_by_id(conn: sqlite3.Connection, registration_id: int):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, event_id, user_name, status, registered_at
        FROM registrations
        WHERE id = ?
        """,
        (registration_id,)
    )
    return cursor.fetchone()


def find_active_registration(conn: sqlite3.Connection, event_id: int, user_name: str):
    cursor = conn.cursor()
    # Only active registrations participate in duplicate-check and cancellation workflows.
    cursor.execute(
        """
        SELECT id
        FROM registrations
        WHERE event_id = ?
          AND user_name = ?
          AND status = 'active'
        """,
        (event_id, user_name)
    )
    return cursor.fetchone()


def cancel_registration(conn: sqlite3.Connection, registration_id: int) -> None:
    cursor = conn.cursor()
    # Soft delete by marking the registration as cancelled so registration history is preserved.
    cursor.execute(
        """
        UPDATE registrations
        SET status = 'cancelled'
        WHERE id = ?
        """,
        (registration_id,)
    )
