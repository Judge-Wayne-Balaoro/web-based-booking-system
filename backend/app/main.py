import asyncio

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import SessionLocal
from .routers import auth, admin, public
from .services.booking_service import expire_all_pending

app = FastAPI(title="Palacio Feliz Booking System API")

# CORS (for vanilla HTML/JS frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation error", "errors": exc.errors()},
    )


# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(public.router, prefix="/api", tags=["public"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
def read_root():
    return {"message": "Palacio Feliz Booking System API is running"}


# Background worker: expire pending bookings automatically
@app.on_event("startup")
async def start_expiry_worker():
    async def worker():
        while True:
            db = SessionLocal()
            try:
                expire_all_pending(db)
            finally:
                db.close()
            await asyncio.sleep(60)  # every 60 seconds

    asyncio.create_task(worker())