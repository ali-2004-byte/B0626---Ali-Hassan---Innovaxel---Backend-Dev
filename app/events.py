from typing import List
from fastapi import APIRouter, Depends
import sqlite3
from app.database import get_db
from app.models import CreateEventRequest, EventResponse
from app.services import create_event_service, list_events_service

router = APIRouter()

@router.post(
    "/events",
    response_model=EventResponse,
    status_code=201,
    summary="Create an event",
    responses={
        400: {"description": "Validation error or missing data"},
        409: {"description": "Event name already exists"},
        422: {"description": "Request validation error"}
    }
)
def create_event(event: CreateEventRequest, conn: sqlite3.Connection = Depends(get_db)):
    return create_event_service(event, conn)

@router.get(
    "/events",
    response_model=List[EventResponse],
    summary="List events",
    responses={
        422: {"description": "Query parameter validation error"}
    }
)
def list_events(upcoming_only: bool = False, sort_by_date: bool = False, conn: sqlite3.Connection = Depends(get_db)):
    return list_events_service(upcoming_only, sort_by_date, conn)
