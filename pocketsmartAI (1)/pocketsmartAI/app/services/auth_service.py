import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from app.config import settings
from app.services.storage_service import storage

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire, 'iat': datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def extract_token_from_request(request: Request) -> Optional[str]:
    # 1. Authorization header: Bearer <token>
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:].strip()
    
    # 2. Session cookie
    cookie_token = request.cookies.get('session_token')
    if cookie_token:
        return cookie_token
        
    return None

def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    token = extract_token_from_request(request)
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or 'sub' not in payload:
        return None
    user = storage.get_user_by_id(payload['sub'])
    return user

def get_current_user_required(request: Request) -> Dict[str, Any]:
    user = get_current_user_optional(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated or session expired',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return user
