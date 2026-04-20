import uuid
import time
from datetime import datetime
from typing import Any, Dict, Optional


def generate_request_id() -> str:
    """Request ID: PRV-{timestamp}-{random}"""
    timestamp = int(time.time())
    random_id = str(uuid.uuid4())[:6]
    return f"PRV-{timestamp}-{random_id}"


def standard_response(
    request_id: str,
    success: bool,
    data: Optional[Any] = None,
    message: str = "",
    status_code: int = 200,
) -> Dict[str, Any]:
    """Standard response format"""
    return {
        "request_id": request_id,
        "success": success,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }


class StandardResponse:
    def __init__(self, request_id: str):
        self.request_id = request_id

    def success(self, data: Any = None, message: str = "") -> Dict[str, Any]:
        return standard_response(self.request_id, True, data, message)

    def error(self, message: str, data: Any = None) -> Dict[str, Any]:
        return standard_response(self.request_id, False, data, message)
