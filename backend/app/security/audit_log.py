from datetime import datetime
import json
import logging
from typing import Any, Dict, Optional

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Configurar el handler para archivo
        handler = logging.FileHandler("audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_auth_event(
        self,
        event_type: str,
        user_id: Optional[int],
        success: bool,
        ip_address: str,
        details: Dict[str, Any]
    ) -> None:
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "success": success,
            "ip_address": ip_address,
            "details": details
        }
        self.logger.info(json.dumps(event))

audit_logger = AuditLogger()
