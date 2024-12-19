from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from . import models, schemas
from dotenv import load_dotenv
import os
from .security.rate_limiter import rate_limiter
from .security.password_validator import password_validator, PasswordValidationError
from .security.mfa import mfa_handler
from .security.audit_log import audit_logger

load_dotenv()

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__min_rounds=12
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    try:
        password_validator.validate(password)
        return pwd_context.hash(password)
    except PasswordValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def get_user(db: Session, email: str):
    return db.query(models.usuario.Usuario).filter(models.usuario.Usuario.email == email).first()

def authenticate_user(
    db: Session,
    username: str,
    password: str,
    mfa_token: Optional[str] = None,
    client_ip: str = "127.0.0.1"
) -> Optional[models.usuario.Usuario]:
    # Verificar rate limiting
    if rate_limiter.is_client_locked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to too many failed attempts"
        )

    user = get_user(db, username)
    if not user:
        audit_logger.log_auth_event(
            "login_failed",
            None,
            False,
            client_ip,
            {"reason": "user_not_found"}
        )
        rate_limiter.record_failed_attempt(client_ip)
        return None
    
    if not verify_password(password, user.hashed_password):
        audit_logger.log_auth_event(
            "login_failed",
            user.id,
            False,
            client_ip,
            {"reason": "invalid_password"}
        )
        rate_limiter.record_failed_attempt(client_ip)
        return None
    
    # Si el usuario tiene MFA habilitado, verificar el token
    if user.mfa_enabled:
        if not mfa_token:
            audit_logger.log_auth_event(
                "login_failed",
                user.id,
                False,
                client_ip,
                {"reason": "mfa_required"}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MFA token required"
            )
        
        if not mfa_handler.verify_totp(user, mfa_token):
            audit_logger.log_auth_event(
                "login_failed",
                user.id,
                False,
                client_ip,
                {"reason": "invalid_mfa"}
            )
            rate_limiter.record_failed_attempt(client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA token"
            )
    
    # Registrar autenticación exitosa
    audit_logger.log_auth_event(
        "login_success",
        user.id,
        True,
        client_ip,
        {"mfa_used": user.mfa_enabled}
    )
    
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.usuario.Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: models.usuario.Usuario = Depends(get_current_user)
) -> models.usuario.Usuario:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def verify_admin(
    current_user: models.usuario.Usuario = Depends(get_current_active_user)
) -> models.usuario.Usuario:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action"
        )
    return current_user
