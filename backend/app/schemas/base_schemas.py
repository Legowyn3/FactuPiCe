from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class EstadoFactura(str, Enum):
    borrador = "borrador"
    emitida = "emitida"
    pagada = "pagada"
    vencida = "vencida"
    anulada = "anulada"

class TipoFactura(str, Enum):
    ordinaria = "ordinaria"
    rectificativa = "rectificativa"
    simplificada = "simplificada"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=100)
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    mfa_enabled: bool = False

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class MFAResponse(BaseModel):
    qr_code: str
    secret: str
