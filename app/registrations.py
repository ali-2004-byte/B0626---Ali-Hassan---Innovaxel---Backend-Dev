from fastapi import APIRouter, Depends
import sqlite3
from app.database import get_db
from app.models import RegisterUserRequest, RegistrationResponse
from app.services import register_user_service, cancel_registration_service

router = APIRouter()


@router.post(
    "/registrations",
    response_model=RegistrationResponse,
    status_code=201,
    summary="Register a user for an event",
    responses={
        400: {"description": "Event is full or user already registered"},
        404: {"description": "Event not found"},
        422: {"description": "Request validation error"}
    }
)
def register_user(request: RegisterUserRequest, conn: sqlite3.Connection = Depends(get_db)):
    return register_user_service(request, conn)


@router.delete(
    "/registrations/{event_id}/{user_name}",
    status_code=200,
    summary="Cancel a registration",
    responses={
        404: {"description": "No active registration found"},
        422: {"description": "Path parameter validation error"}
    }
)
def cancel_registration(event_id: int, user_name: str, conn: sqlite3.Connection = Depends(get_db)):
    return cancel_registration_service(event_id, user_name, conn)
