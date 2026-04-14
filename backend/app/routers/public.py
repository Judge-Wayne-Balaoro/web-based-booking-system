from datetime import date

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_db
from ..services.booking_service import is_date_reserved, create_pending_booking
from ..services.file_service import save_receipt
from ..utils.response import ok

router = APIRouter(tags=["public"])


@router.get("/availability")
def check_availability(event_date: date, db: Session = Depends(get_db)):
    reserved = is_date_reserved(db, event_date)
    return ok({"event_date": str(event_date), "available": not reserved})


@router.post("/bookings/upload")
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
    receipt_path = save_receipt(receipt)

    booking = create_pending_booking(
        db,
        guest_name=guest_name,
        contact_number=contact_number,
        email=email,
        event_date=event_date,
        pax=pax,
        payment_method=payment_method,
        deposit_amount=deposit_amount,
        receipt_path=receipt_path,
    )

    # return a frontend-friendly subset (stable contract)
    return ok(
        {
            "id": booking.id,
            "booking_code": booking.booking_code,
            "status": booking.status.value if hasattr(booking.status, "value") else str(booking.status),
            "event_date": str(booking.event_date),
            "pax": booking.pax,
        },
        status_code=201,
    )


@router.get("/track/{booking_code}")
def track_booking(booking_code: str, db: Session = Depends(get_db)):
    stmt = select(models.Booking).where(models.Booking.booking_code == booking_code)
    booking = db.execute(stmt).scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return ok(
        {
            "booking_code": booking.booking_code,
            "status": booking.status.value if hasattr(booking.status, "value") else str(booking.status),
            "event_date": str(booking.event_date),
            "pax": booking.pax,
        }
    )