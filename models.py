from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(15), unique=True, nullable=False) 
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship: One user can have an account
    account = relationship("Account", back_populates="owner", uselist=False)

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    account_number = Column(String(20), unique=True, nullable=False)
    balance = Column(Numeric(15, 2), default=0.00)
    currency = Column(String(3), default="PKR")

    owner = relationship("User", back_populates="account")

class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    sender_account_id = Column(Integer, ForeignKey("accounts.id"))
    receiver_account_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Numeric(15, 2), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    sender = relationship("Account", foreign_keys=[sender_account_id])
    receiver = relationship("Account", foreign_keys=[receiver_account_id])

class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    consumer_id = Column(String, unique=True, index=True)
    company_name = Column(String)  # e.g., LESCO, SNGPL
    amount = Column(Float)
    is_paid = Column(Boolean, default=False)