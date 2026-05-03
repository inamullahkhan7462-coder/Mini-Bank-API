from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Tell passlib we want to use bcrypt (the industry standard)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """Turns '1234' into a long scrambled string"""
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Checks if the entered PIN matches the scrambled one in the DB"""
    return pwd_context.verify(plain_password, hashed_password)


# Settings for the token
SECRET_KEY = "inam_bank_secret_key_786" # Change this to a random string
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token expires in 30 minutes for security

def create_access_token(data: dict):
    to_encode = data.copy()
    
    # Set the expiration time
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Create the encoded JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt