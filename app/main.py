from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date

from .database import engine, Base
from . import models, schemas
from .deps import get_db

from fastapi import File, UploadFile, Form
import os
from uuid import uuid4


app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Palacio Feliz Booking System API is running"}


@app.get("/api/availability")
def check_availability(event_date: date, db: Session = Depends(get_db)):
    stmt = select(models.Booking).where(
        models.Booking.event_date == event_date,
        models.Booking.status == "RESERVED",
    )
    existing = db.execute(stmt).scalar_one_or_none()
    return {"event_date": str(event_date), "available": existing is None}


@app.post("/api/bookings/upload", response_model=schemas.BookingOut)
def create_booking_with_receipt(
    guest_name: str = Form(...),
    contact_number: str = Form(...),
    email: str = Form(...),
    event_date: date = Form(...),
    pax: int = Form(...),
    payment_method: str = Form(...),
    deposit_amount: int = Form(...),
    receipt: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # basic pax/deposit rules (we’ll improve later)
    if pax > 50:
        raise HTTPException(status_code=422, detail="Maximum allowed pax is 50")
    if deposit_amount < 2000:
        raise HTTPException(status_code=422, detail="Minimum deposit is ₱2000")

    # prevent booking if RESERVED exists
    stmt = select(models.Booking).where(
        models.Booking.event_date == event_date,
        models.Booking.status == "RESERVED",
    )
    if db.execute(stmt).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Date is already reserved")

    # save file
    os.makedirs("media/receipts", exist_ok=True)
    ext = os.path.splitext(receipt.filename)[1].lower()
    filename = f"{uuid4().hex}{ext}"
    filepath = os.path.join("media", "receipts", filename)

    with open(filepath, "wb") as f:
        f.write(receipt.file.read())

    booking = models.Booking(
        guest_name=guest_name,
        contact_number=contact_number,
        email=email,
        event_date=event_date,
        pax=pax,
        payment_method=payment_method.upper(),
        deposit_amount=deposit_amount,
        receipt_path=filepath,
        status="PENDING",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@app.post("/api/admin/bookings/{booking_id}/approve")
def approve_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(models.Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = "RESERVED"
    db.commit()
    return {"ok": True, "booking_id": booking_id, "status": "RESERVED"}