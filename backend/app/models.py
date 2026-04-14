import enum
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, UniqueConstraint 
from datetime import datetime
from .database import Base
from sqlalchemy import Boolean
from passlib.context import CryptContext

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    RESERVED = "RESERVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    email = Column(String, nullable=False)

    event_date = Column(Date, nullable=False)
    pax = Column(Integer, nullable=False)

    payment_method = Column(String, nullable=False) 
    deposit_amount = Column(Integer, nullable=False)

    status = Column(
    Enum(BookingStatus, name="booking_status"),
    nullable=False,
    default=BookingStatus.PENDING,
)

    created_at = Column(DateTime, default=datetime.utcnow)

    receipt_path = Column(String, nullable=True)

    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    rejection_reason = Column(String, nullable=True)
    cancellation_reason = Column(String, nullable=True)
    
    hold_expires_at = Column(DateTime, nullable=True)
    booking_code = Column(String(20), unique=True, nullable=False, index=True)