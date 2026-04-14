from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from .. import models
from ..deps import get_db, require_admin
from ..services.booking_service import (
    approve_booking as approve_booking_service,
    reject_booking as reject_booking_service,
    cancel_booking as cancel_booking_service,
)
from ..utils.response import ok
from sqlalchemy import func

router = APIRouter(
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


def _status_to_str(status) -> str:
    return status.value if hasattr(status, "value") else str(status)


@router.post("/bookings/{booking_id}/approve")
def approve_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = approve_booking_service(db, booking_id)
    return ok(
        {
            "booking_id": booking_id,
            "status": _status_to_str(booking.status),
        }
    )


@router.post("/bookings/{booking_id}/reject")
def reject_booking(
    booking_id: int,
    reason: str | None = Body(default=None, embed=True),
    db: Session = Depends(get_db),
):
    booking = reject_booking_service(db, booking_id, reason=reason)
    return ok(
        {
            "booking_id": booking_id,
            "status": _status_to_str(booking.status),
        }
    )


@router.post("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    reason: str | None = Body(default=None, embed=True),
    db: Session = Depends(get_db),
):
    booking = cancel_booking_service(db, booking_id, reason=reason)
    return ok(
        {
            "booking_id": booking_id,
            "status": _status_to_str(booking.status),
        }
    )


@router.get("/bookings")
def list_bookings(
    status: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10

    base_stmt = select(models.Booking)

    if status:
        status_up = status.upper()
        allowed = {s.value for s in models.BookingStatus}
        if status_up not in allowed:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status. Allowed: {sorted(allowed)}",
            )
        base_stmt = base_stmt.where(
            models.Booking.status == models.BookingStatus(status_up)
        )

    # total count
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = db.execute(count_stmt).scalar()

    # pagination
    stmt = (
        base_stmt
        .order_by(models.Booking.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    bookings = db.execute(stmt).scalars().all()

    items = [
        {
            "id": b.id,
            "booking_code": b.booking_code,
            "guest_name": b.guest_name,
            "event_date": str(b.event_date),
            "pax": b.pax,
            "status": b.status.value,
            "deposit_amount": b.deposit_amount,
            "created_at": b.created_at.isoformat(),
        }
        for b in bookings
    ]

    total_pages = (total + page_size - 1) // page_size if total else 0

    return ok(
        {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    )