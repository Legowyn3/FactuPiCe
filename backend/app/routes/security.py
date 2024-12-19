from fastapi import APIRouter, HTTPException, Request
from app.security.rate_limiter import rate_limiter
from typing import Dict

router = APIRouter()

@router.get("/rate-limit/status/{username}")
def get_rate_limit_status(username: str, request: Request) -> Dict:
    """
    Obtener el estado actual del rate limiting para un usuario
    """
    client_ip = request.client.host
    status = rate_limiter.get_client_status(client_ip)
    return status
