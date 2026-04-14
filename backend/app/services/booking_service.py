from datetime import date, datetime, timedelta
import random
import string

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import sqlalchemy as sa

from .. import models

HOLD_MINUTES = 1

ALLOWED_TRANSITIONS = {
    models.BookingStatus.PENDING: {
        models.BookingStatus.RESERVED,
        models.BookingStatus.REJECTED,
        models.BookingStatus.CANCELLED,
    },
    models.BookingStatus.RESERVED: {
        models.BookingStatus.CANCELLED,
    },
    models.BookingStatus.REJECTED: set(),
    models.BookingStatus.CANCELLED: set(),
    models.BookingStatus.EXPIRED: set(),
}


def generate_booking_code() -> str:
    return "PF-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def _next_booking_code(db: Session) -> str:
    """
    If you want sequential codes (requires booking_code_seq in DB),
    you can switch create_pending_booking() to use this.
    """
    seq = db.execute(sa.text("SELECT nextval('booking_code_seq')")).scalar_one()
    year = datetime.utcnow().year
    return f"PF-{year}-{seq:06d}"


def _expire_pending_for_date(db: Session, event_date: date) -> int:
    """
    Expires PENDING bookings for a specific date whose hold_expires_at has passed.
    Returns number expired.
    """
    now = datetime.utcnow()

    stmt = select(models.Booking).where(
        models.Booking.event_date == event_date,
        models.Booking.status == models.BookingStatus.PENDING,
        models.Booking.hold_expires_at.isnot(None),
        models.Booking.hold_expires_at < now,
    )

    expired = db.execute(stmt).scalars().all()
    for b in expired:
        b.status = models.BookingStatus.EXPIRED

    if expired:
        db.commit()

    return len(expired)


def expire_all_pending(db: Session) -> int:
    """
    Expires ALL pending bookings whose hold_expires_at has passed.
    Useful for a background worker.
    Returns number expired.
    """
    now = datetime.utcnow()

    stmt = select(models.Booking).where(
        models.Booking.status == models.BookingStatus.PENDING,
        models.Booking.hold_expires_at.isnot(None),
        models.Booking.hold_expires_at < now,
    )

    expired = db.execute(stmt).scalars().all()
    for b in expired:
        b.status = models.BookingStatus.EXPIRED

    if expired:
        db.commit()

    return len(expired)


def is_date_reserved(db: Session, event_date: date) -> bool:
    stmt = select(models.Booking).where(
        models.Booking.event_date == event_date,
        models.Booking.status == models.BookingStatus.RESERVED,
    )
    return db.execute(stmt).scalar_one_or_none() is not None


def _has_active_hold(db: Session, event_date: date) -> bool:
    now = datetime.utcnow()
    stmt = select(models.Booking).where(
        models.Booking.event_date == event_date,
        models.Booking.status == models.BookingStatus.PENDING,
        models.Booking.hold_expires_at.isnot(None),
        models.Booking.hold_expires_at > now,
    )
    return db.execute(stmt).scalar_one_or_none() is not None


def create_pending_booking(
    db: Session,
    *,
    guest_name: str,
    contact_number: str,
    email: str,
    event_date: date,
    pax: int,
    payment_method: str,
    deposit_amount: int,
    receipt_path: str,
):
    # Basic validation
    if pax > 50:
        raise HTTPException(status_code=422, detail="Maximum allowed pax is 50")

    if deposit_amount < 2000:
        raise HTTPException(status_code=422, detail="Minimum deposit is ₱2000")

    # If already RESERVED, block
    if is_date_reserved(db, event_date):
        raise HTTPException(status_code=409, detail="Date is already reserved")

    # Expire old holds for that date
    _expire_pending_for_date(db, event_date)

    # If still actively held, block
    if _has_active_hold(db, event_date):
        raise HTTPException(
            status_code=409,
            detail="Date is temporarily on hold (pending verification). Try again later.",
        )

    # Create new hold window (UTC naive)
    now = datetime.utcnow()
    hold_until = now + timedelta(minutes=HOLD_MINUTES)

    booking = models.Booking(
        booking_code=generate_booking_code(),  # or _next_booking_code(db)
        guest_name=guest_name.strip(),
        contact_number=contact_number.strip(),
        email=email.strip().lower(),
        event_date=event_date,
        pax=pax,
        payment_method=payment_method.upper(),
        deposit_amount=deposit_amount,
        receipt_path=receipt_path,
        status=models.BookingStatus.PENDING,
        hold_expires_at=hold_until,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def approve_booking(db: Session, booking_id: int):
    booking = db.get(models.Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    try:
        return _change_status(
            db,
            booking,
            models.BookingStatus.RESERVED,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Date already reserved")


def reject_booking(db: Session, booking_id: int, reason=None):
    booking = db.get(models.Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return _change_status(
        db,
        booking,
        models.BookingStatus.REJECTED,
        reason=reason,
    )


def cancel_booking(db: Session, booking_id: int, reason=None):
    booking = db.get(models.Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return _change_status(
        db,
        booking,
        models.BookingStatus.CANCELLED,
        reason=reason,
    )


def _change_status(db: Session, booking, new_status, *, reason=None):
    current = booking.status

    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current} → {new_status}",
        )

    booking.status = new_status
    now = datetime.utcnow()

    if new_status == models.BookingStatus.RESERVED:
        booking.approved_at = now
        booking.hold_expires_at = None

    elif new_status == models.BookingStatus.REJECTED:
        booking.rejected_at = now
        booking.rejection_reason = reason
        booking.hold_expires_at = None

    elif new_status == models.BookingStatus.CANCELLED:
        booking.cancelled_at = now
        booking.cancellation_reason = reason
        booking.hold_expires_at = None

    db.commit()
    db.refresh(booking)
    return booking