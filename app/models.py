from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime
from .database import Base

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

    status = Column(String, default="PENDING")

    created_at = Column(DateTime, default=datetime.utcnow)

    receipt_path = Column(String, nullable=True)