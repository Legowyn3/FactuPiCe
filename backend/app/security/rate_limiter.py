from datetime import datetime, timedelta
from typing import Dict, List
import threading

class RateLimiter:
    def __init__(self, max_attempts: int = 5, lockout_time: int = 15):
        self.max_attempts = max_attempts
        self.lockout_time = timedelta(minutes=lockout_time)
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.lock = threading.Lock()

    def record_failed_attempt(self, client_ip: str) -> None:
        with self.lock:
            current_time = datetime.utcnow()
            if client_ip not in self.failed_attempts:
                self.failed_attempts[client_ip] = []
            self.failed_attempts[client_ip].append(current_time)
            self._cleanup_old_attempts(client_ip)

    def is_client_locked(self, client_ip: str) -> bool:
        with self.lock:
            if client_ip not in self.failed_attempts:
                return False
            
            self._cleanup_old_attempts(client_ip)
            return len(self.failed_attempts[client_ip]) >= self.max_attempts

    def _cleanup_old_attempts(self, client_ip: str) -> None:
        current_time = datetime.utcnow()
        self.failed_attempts[client_ip] = [
            attempt 
            for attempt in self.failed_attempts[client_ip] 
            if current_time - attempt < self.lockout_time
        ]
        if not self.failed_attempts[client_ip]:
            del self.failed_attempts[client_ip]

    def reset_attempts(self, client_ip: str) -> None:
        """Resetear intentos fallidos después de login exitoso"""
        with self.lock:
            if client_ip in self.failed_attempts:
                del self.failed_attempts[client_ip]

rate_limiter = RateLimiter()
