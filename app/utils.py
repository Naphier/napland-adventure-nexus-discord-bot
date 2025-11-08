import json
from typing import Any, Dict


def build_response(body: Any, status_code: int = 200) -> Dict[str, Any]:
    """Construct a standard Lambda proxied HTTP response."""
    serialized_body = _serialize_body(body)
    return {
        "statusCode": status_code,
        "body": serialized_body,
        "headers": {"Content-Type": "application/json"},
    }


def _serialize_body(body: Any) -> str:
    if isinstance(body, str):
        return body
    try:
        return json.dumps(body)
    except TypeError:
        return str(body)

