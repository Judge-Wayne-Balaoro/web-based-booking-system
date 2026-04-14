from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..deps import get_db
from ..models import Admin
from ..core.security import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginIn(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    admin = db.execute(select(Admin).where(Admin.username == data.username)).scalar_one_or_none()
    if not admin or not verify_password(data.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(subject=admin.username)
    return {"access_token": token, "token_type": "bearer"}