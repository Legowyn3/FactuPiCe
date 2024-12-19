import pyotp
import qrcode
from io import BytesIO
import base64
from typing import Optional
from ..models.usuario import Usuario

class MFAHandler:
    def __init__(self):
        self.issuer_name = "FactuPiCe"

    def generate_secret(self) -> str:
        return pyotp.random_base32()

    def generate_qr_code(self, email: str, secret: str) -> str:
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            email,
            issuer_name=self.issuer_name
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def verify_totp(self, user: Usuario, token: str) -> bool:
        if not user.mfa_secret:
            return False
        
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(token)

mfa_handler = MFAHandler()
