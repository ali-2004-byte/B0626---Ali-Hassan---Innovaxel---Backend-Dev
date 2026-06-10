import sqlite3


def open_connection():
    # Enable Row objects so columns can be accessed by name:
    # row["id"] instead of row[0]
    conn = sqlite3.connect("data/events.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enforce foreign key constraints in SQLite. (Disabled by default in SQLite.)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    # FastAPI dependency that guarantees connections are closed after each request.
    conn = open_connection()
    try:
        yield conn
    finally:
        conn.close()


def create_tables():
    conn = open_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL UNIQUE,
        total_seats INTEGER NOT NULL CHECK(total_seats > 0),
        event_date  TEXT    NOT NULL,
        created_at  TEXT    DEFAULT (datetime('now'))
        );
        """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
      id             INTEGER PRIMARY KEY AUTOINCREMENT,
      event_id       INTEGER NOT NULL REFERENCES events(id),
      user_name      TEXT    NOT NULL,
      status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'cancelled')),
      registered_at  TEXT    DEFAULT (datetime('now'))
    );
    """)
    # Preventing duplicate active registrations 
    # while still allowing users to register again after cancelling
    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS unique_active_registration
    ON registrations(event_id, user_name)
    WHERE status = 'active';
    """)
    conn.commit()
    conn.close()