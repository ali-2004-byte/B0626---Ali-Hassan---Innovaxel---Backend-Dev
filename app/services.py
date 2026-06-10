import sqlite3
from fastapi import HTTPException, status
from app.models import CreateEventRequest, RegisterUserRequest
from app.repositories import (
    cancel_registration,
    count_active_registrations,
    find_active_registration,
    get_event_by_id,
    get_registration_by_id,
    insert_event,
    insert_registration,
    list_events,
)


def create_event_service(event: CreateEventRequest, conn: sqlite3.Connection):
    try:
        event_id = insert_event(
            conn,
            event.name,
            event.total_seats,
            event.event_date.isoformat(),
        )
        conn.commit()

        return {
            "id": event_id,
            "name": event.name,
            "event_date": event.event_date,
            "total_seats": event.total_seats,
            "total_registrations": 0,
            "available_seats": event.total_seats,
        }

    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event name already exists"
        )


def list_events_service(upcoming_only: bool, sort_by_date: bool, conn: sqlite3.Connection):
    rows = list_events(conn, upcoming_only, sort_by_date)
    return [dict(row) for row in rows]


def register_user_service(request: RegisterUserRequest, conn: sqlite3.Connection):
    try:
        conn.execute("BEGIN EXCLUSIVE")
        # Lock the database so seat availability check and registration
        # insertion occur atomically, preventing overbooking.
        event = get_event_by_id(conn, request.event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        active_registration = find_active_registration(conn, request.event_id, request.user_name)
        if active_registration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already registered for this event"
            )

        active_count = count_active_registrations(conn, request.event_id)
        if active_count >= event["total_seats"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event is full"
            )

        registration_id = insert_registration(
            conn,
            request.event_id,
            request.user_name,
        )
        registration = get_registration_by_id(conn, registration_id)
        conn.commit()
        return dict(registration)

    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already registered for this event"
        )

    except HTTPException:
        conn.rollback()
        raise

    except Exception:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


def cancel_registration_service(event_id: int, user_name: str, conn: sqlite3.Connection):
    registration = find_active_registration(conn, event_id, user_name)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active registration found"
        )
    # Seat availability updates automatically because
    # available seats are derived from active registrations.
    cancel_registration(conn, registration["id"])
    conn.commit()

    return {"message": "Registration cancelled successfully"}
