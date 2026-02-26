from pydantic import BaseModel, EmailStr, field_validator
from datetime import date

class BookingCreate(BaseModel):
    guest_name: str
    contact_number: str
    email: EmailStr
    event_date: date
    pax: int
    payment_method: str  # "GCASH" or "CASH"
    deposit_amount: int

    @field_validator("pax")
    @classmethod
    def validate_pax(cls, v: int):
        if v < 1:
            raise ValueError("pax must be at least 1")
        if v > 50:
            raise ValueError("Maximum allowed pax is 50")
        return v

    @field_validator("deposit_amount")
    @classmethod
    def validate_deposit(cls, v: int):
        if v < 2000:
            raise ValueError("Minimum deposit is ₱2000")
        return v


class BookingOut(BaseModel):
    id: int
    guest_name: str
    email: EmailStr
    event_date: date
    pax: int
    status: str

    class Config:
        from_attributes = True