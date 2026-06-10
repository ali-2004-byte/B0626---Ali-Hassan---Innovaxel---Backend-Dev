from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.database import create_tables 
from app.events import router as events_router
from app.registrations import router as registrations_router

# Application lifespan hook ensures the database schema exists before requests are handled.
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Event Registration API",
)
app.include_router(events_router)
app.include_router(registrations_router)


@app.exception_handler(Exception)
def handle_unhandled_exceptions(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )