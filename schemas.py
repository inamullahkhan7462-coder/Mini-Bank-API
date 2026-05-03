from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

# This is what we expect when a user signs up
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str = Field(..., pattern=r"^\d{11}$") # Forces 11 digits (e.g., 03001234567)
    # We use Field to force exactly 4 digits using regex (Regular Expression)
    password: str = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$")

# This is what we send back to the user (notice we DON'T send the password back!)
class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

# This is for creating a transfer
class TransferCreate(BaseModel):
    receiver_account_number: str
    amount: Decimal

class UserLogin(BaseModel):
    email: EmailStr
    password: str # This will be the 4-digit PIN

class Token(BaseModel):
    access_token: str
    token_type: str

class TransferDetail(BaseModel):
    id: int
    amount: float
    timestamp: datetime
    sender_name: str # New field
    receiver_name: str # New field

    class Config:
        from_attributes = True