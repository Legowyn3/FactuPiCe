from fastapi import Request, HTTPException
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import os
from dotenv import load_dotenv

load_dotenv()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        hsts_max_age: int = 31536000,  # 1 año
        include_subdomains: bool = True,
        preload: bool = True,
    ):
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.include_subdomains = include_subdomains
        self.preload = preload

    async def dispatch(self, request: Request, call_next):
        # Forzar HTTPS en producción
        if os.getenv('ENVIRONMENT') == 'production' and request.url.scheme != 'https':
            return Response(
                status_code=301,
                headers={'Location': str(request.url).replace('http://', 'https://', 1)}
            )

        response = await call_next(request)

        # Cabeceras de seguridad
        headers = {
            # HSTS
            'Strict-Transport-Security': f'max-age={self.hsts_max_age}' + 
                                       ('; includeSubDomains' if self.include_subdomains else '') +
                                       ('; preload' if self.preload else ''),
            
            # Content Security Policy
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Permitir scripts inline para desarrollo
                "style-src 'self' 'unsafe-inline'; "  # Permitir estilos inline para desarrollo
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "form-action 'self';"
            ),
            
            # Prevenir XSS
            'X-XSS-Protection': '1; mode=block',
            
            # No permitir que el sitio sea embebido en iframes
            'X-Frame-Options': 'DENY',
            
            # Forzar el tipo MIME
            'X-Content-Type-Options': 'nosniff',
            
            # Referrer Policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Feature Policy
            'Permissions-Policy': (
                'accelerometer=(), '
                'camera=(), '
                'geolocation=(), '
                'gyroscope=(), '
                'magnetometer=(), '
                'microphone=(), '
                'payment=(), '
                'usb=()'
            ),
            
            # Cache Control
            'Cache-Control': 'no-store, max-age=0',
        }

        # Agregar cabeceras de seguridad a la respuesta
        for key, value in headers.items():
            response.headers[key] = value

        return response

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if os.getenv('ENVIRONMENT') == 'production' and request.url.scheme != 'https':
            return Response(
                status_code=301,
                headers={'Location': str(request.url).replace('http://', 'https://', 1)}
            )
        return await call_next(request)
