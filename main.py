from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine, Base
from fastapi.middleware.cors import CORSMiddleware  # <--- Add this import
import random
from fastapi.responses import JSONResponse # <--- Add this
from decimal import Decimal
from utils import hash_password
from utils import verify_password, create_access_token # Add these imports at the top
from jose import jwt, JWTError
from utils import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
oauth2_scheme = APIKeyHeader(name="Authorization")
Base.metadata.create_all(bind=engine)
# Create the FastAPI app
app = FastAPI(
    title="Inam's Digital Bank API",
    description="A secure Pakistani Fintech API for peer-to-peer transfers and bill payments.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all websites (like Lovable) to access your API
    allow_credentials=True,
    allow_methods=["*"],  # This allows GET, POST, etc.
    allow_headers=["*"],  # This allows tokens/headers
)
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Our team is looking into it."},
    )
# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- THE SIGNUP ENDPOINT ---
# @app.post("/signup", response_model=schemas.UserOut)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     # 1. Check if user already exists
#     db_user = db.query(models.User).filter(models.User.email == user.email).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # 2. Hash the password (for now we use a simple placeholder, we will add the real hasher next!)
#     hashed_password = user.password + "not_secure_yet" 
    
#     # 3. Create the User object
#     new_user = models.User(
#         full_name=user.full_name,
#         email=user.email,
#         password_hash=hashed_password
#     )
    
#     # 4. Save to Database
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
    
#     return new_user

@app.post("/signup", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # ... (existing check for email) ...
    hashed_pin = hash_password(user.password)
    # 1. Create the User
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        password_hash=hashed_pin # We'll fix hashing next
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 2. AUTOMATICALLY create an Account for this new user
    new_account = models.Account(
        user_id=new_user.id,
        account_number=user.phone_number, # Use the user's phone number as the account number
        balance=5000.00, # Let's give them a 5000 PKR starting bonus!
        currency="PKR"
    )
    db.add(new_account)
    db.commit()

    return new_user


@app.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # 1. Look for the user in the database
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    
    # 2. Check if user exists and if the PIN is correct
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=403, detail="Invalid Credentials")

    # 3. Create the Digital ID Card (JWT)
    access_token = create_access_token(data={"user_id": user.id})

    # 4. Hand the token back to the user
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.post("/transfer")
def make_transfer(
    transfer_data: schemas.TransferCreate, 
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user) # The JWT 'Lock' is now active
):
    # 1. Identify the Sender automatically using the Token
    # We find the user first, then access their linked account
    sender_user = db.query(models.User).filter(models.User.id == current_user_id).first()
    sender_acc = sender_user.account 
    check_daily_limit(db, sender_acc.id, transfer_data.amount)
    if not sender_acc:
        raise HTTPException(status_code=404, detail="Sender account not found")

    # 2. Get the Receiver by the phone number provided in the request
    receiver_acc = db.query(models.Account).filter(
        models.Account.account_number == transfer_data.receiver_account_number
    ).first()

    if not receiver_acc:
        raise HTTPException(status_code=404, detail="Receiver account not found")

    # 3. Security Check: Prevent sending money to yourself
    if sender_acc.id == receiver_acc.id:
        raise HTTPException(status_code=400, detail="Cannot transfer money to your own account")

    # 4. Check Balance
    if sender_acc.balance < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # 5. Perform the math (The Transaction)
    sender_acc.balance -= transfer_data.amount
    receiver_acc.balance += transfer_data.amount

    # 6. Record the transfer in the ledger
    new_transfer = models.Transfer(
        sender_account_id=sender_acc.id,
        receiver_account_id=receiver_acc.id,
        amount=transfer_data.amount
    )
    
    db.add(new_transfer)
    db.commit() 
    db.refresh(sender_acc) # Refresh to get the updated balance from DB

    return {
        "status": "Success",
        "message": f"Transfer of {transfer_data.amount} PKR successful",
        "remaining_balance": sender_acc.balance
    }


# This checks if the user's ID Card is real
def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid ID Card")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
@app.get("/my-transfers")
def get_transfers(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user)):
    # 1. Get the current user's account
    user_account = db.query(models.Account).filter(models.Account.user_id == current_user_id).first()
    
    # 2. Get the raw history (same as before)
    raw_history = db.query(models.Transfer).filter(
        (models.Transfer.sender_account_id == user_account.id) | 
        (models.Transfer.receiver_account_id == user_account.id)
    ).all()
    
    # 3. Format the data for the User (The "Statement" logic)
    statement = []
    for t in raw_history:
        # Check if the current user was the one sending or receiving
        is_sender = t.sender_account_id == user_account.id
        
        statement.append({
            # "transaction_id": t.id,
            "amount": t.amount,
            "timestamp": t.timestamp,
            "sender_name": t.sender.owner.full_name,   # Follows Transfer -> Account -> User
            "receiver_name": t.receiver.owner.full_name,
            "transaction_type": "Debit (Sent)" if is_sender else "Credit (Received)"
        })
    
    return statement


@app.get("/balance")
def check_balance(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user)):
    user_account = db.query(models.Account).filter(models.Account.user_id == current_user_id).first()
    return {
        "account_holder": user_account.owner.full_name,
        "account_number": user_account.account_number,
        "current_balance": user_account.balance,
        "currency": "PKR"
    }



def check_daily_limit(db: Session, sender_account_id: int, new_amount: float):
    # 1. Define the timeframe (last 24 hours)
    twenty_four_hours_ago = datetime.now() - timedelta(days=1)
    
    # 2. Sum up all transfers sent by this user in the last 24 hours
    total_sent_today = db.query(func.sum(models.Transfer.amount)).filter(
        models.Transfer.sender_account_id == sender_account_id,
        models.Transfer.timestamp >= twenty_four_hours_ago
    ).scalar() or 0 # 'or 0' handles the case where no transfers were made
    
    # 3. Check if the new transfer exceeds the 50,000 PKR limit
    limit = 50000.0
    if (float(total_sent_today) + new_amount) > limit:
        remaining = limit - float(total_sent_today)
        raise HTTPException(
            status_code=400, 
            detail=f"Daily limit exceeded. You can only send {remaining} PKR more today."
        )
    


@app.get("/fetch-bill/{company}/{consumer_id}")
def fetch_bill(company: str, consumer_id: str, db: Session = Depends(get_db)):
    bill = db.query(models.Bill).filter(
        models.Bill.company_name == company.upper(), 
        models.Bill.consumer_id == consumer_id
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    return bill



from decimal import Decimal # Add this to your imports at the top!

@app.post("/pay-bill/{company}/{consumer_id}")
def pay_utility_bill(company: str, consumer_id: str, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user)):
    # 1. Find the bill
    bill = db.query(models.Bill).filter(
        models.Bill.company_name == company.upper(), 
        models.Bill.consumer_id == consumer_id
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="Bill record not found")
    if bill.is_paid:
        raise HTTPException(status_code=400, detail="This bill is already paid")

    # 2. Find User Account
    user_acc = db.query(models.Account).filter(models.Account.user_id == current_user_id).first()
    if not user_acc:
        raise HTTPException(status_code=404, detail="Account not found")

    # 3. Convert bill.amount to Decimal for precise banking math
    bill_amount_decimal = Decimal(str(bill.amount))

    # 4. Check Balance
    if user_acc.balance < bill_amount_decimal:
        raise HTTPException(status_code=400, detail="Insufficient balance to pay this bill")

    # 5. Process Payment
    user_acc.balance -= bill_amount_decimal
    bill.is_paid = True
    
    # 6. Commit and Refresh
    db.commit()
    db.refresh(user_acc) # Refresh to get the updated balance from the DB

    return {
        "status": "Success",
        "message": f"Successfully paid {bill.amount} PKR to {company}",
        "new_balance": float(user_acc.balance) # Convert back to float just for the JSON response
    }