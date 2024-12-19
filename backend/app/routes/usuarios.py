from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from ..database import get_db
from ..models import Usuario
from ..schemas.usuario import UsuarioCreate, Usuario as UsuarioSchema, Token, LoginForm, MFASetup
from .. import auth
from ..security.mfa import mfa_handler
import traceback

router = APIRouter(prefix="/api")

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: LoginForm,
    db: Session = Depends(get_db)
):
    try:
        # Verificar credenciales del usuario
        user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
        if not user or not auth.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar MFA si está habilitado
        if user.mfa_enabled:
            if not form_data.mfa_token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="MFA token required"
                )
            
            if not mfa_handler.verify_totp(user, form_data.mfa_token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA token"
                )
        
        # Generar token JWT
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/usuarios", response_model=UsuarioSchema)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        # Verificar si el usuario ya existe
        db_user = auth.get_user(db, email=usuario.email)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email ya registrado"
            )
        
        # Crear el nuevo usuario
        hashed_password = auth.get_password_hash(usuario.password)
        db_user = Usuario(
            email=usuario.email,
            hashed_password=hashed_password,
            nombre=usuario.nombre,
            apellidos=usuario.apellidos,
            telefono=usuario.telefono,
            es_admin=usuario.es_admin,
            es_activo=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear usuario: {str(e)}"
        )

@router.post("/usuarios/mfa/setup", response_model=MFASetup)
async def setup_mfa(form_data: LoginForm, db: Session = Depends(get_db)):
    try:
        # Verificar credenciales del usuario
        user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
        if not user or not auth.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        # Generar secreto MFA y URL para QR
        secret, otpauth_url = mfa_handler.setup_mfa(db, user)
        
        return {
            "secret": secret,
            "otpauth_url": otpauth_url
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
