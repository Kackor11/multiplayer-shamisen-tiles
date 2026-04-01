from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
import bcrypt

# --- KONFIGURACJA ---
SECRET_KEY = "bardzo-tajny-klucz"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- FUNKCJE POMOCNICZE ---
"""Utworzenie bezpiecznego hash z hasla uzywajac bcrypt"""
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    
    # Generowanie 'soli' oraz hashowanie
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    
    return hashed.decode('utf-8')

"""Sprawdzenie czy podane haslo pasuje do hasha w bazie"""
def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    # Sprawdzenie zgodnosci
    return bcrypt.checkpw(pwd_bytes, hash_bytes)

"""Generowanie tokenu JWT (JSON Web Token), ktory klient gry bedzie wysylac."""
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
