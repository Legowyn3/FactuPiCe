import re
from typing import List

class PasswordValidationError(Exception):
    pass

class PasswordValidator:
    def __init__(self):
        self.min_length = 12
        self.min_lowercase = 1
        self.min_uppercase = 1
        self.min_digits = 1
        self.min_special = 1
        self.special_chars = "!@#$%^&*(),.?\":{}|<>"

    def validate(self, password: str) -> bool:
        errors: List[str] = []

        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")

        if len(re.findall(r'[a-z]', password)) < self.min_lowercase:
            errors.append("Password must contain at least one lowercase letter")

        if len(re.findall(r'[A-Z]', password)) < self.min_uppercase:
            errors.append("Password must contain at least one uppercase letter")

        if len(re.findall(r'\d', password)) < self.min_digits:
            errors.append("Password must contain at least one digit")

        if len(re.findall(f'[{re.escape(self.special_chars)}]', password)) < self.min_special:
            errors.append("Password must contain at least one special character")

        if errors:
            raise PasswordValidationError("\n".join(errors))

        return True

password_validator = PasswordValidator()
