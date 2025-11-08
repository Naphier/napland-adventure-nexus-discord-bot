import json
import os
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

try:
    from logger import Logger
    from log_hours_handler import LogHoursHandler
    from display_handler import DisplayHandler
    from database_interface import DatabaseInterface
    from discord_utils import reply, extract_user_id, interaction_response
except ImportError:  # pragma: no cover
    from app.logger import Logger
    from app.log_hours_handler import LogHoursHandler
    from app.display_handler import DisplayHandler
    from app.database_interface import DatabaseInterface
    from app.discord_utils import reply, extract_user_id, interaction_response

PUBLIC_KEY = os.getenv("PUBLIC_KEY")
_database = DatabaseInterface()
_log_hours_handler = LogHoursHandler(_database)
_display_handler = DisplayHandler(_database)
LOG = Logger(__file__)

def lambda_handler(event, context):
    if _is_eventbridge_event(event):
        return handle_display_event(event)

    if "body" not in event:
        LOG.error("Discord interaction payload missing body")
        return _error_response("Invalid request payload")

    body = json.loads(event["body"])
    signature = event["headers"]["x-signature-ed25519"]
    timestamp = event["headers"]["x-signature-timestamp"]
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    message = timestamp + event["body"]

    try:
        verify_key.verify(message.encode(), signature=bytes.fromhex(signature))
    except BadSignatureError:
        return {
            "statusCode": 401,
            "body": "Invalid request signature",
            "headers": {
                "Content-Type": "application/json"
            }
        }
    
    t = body["type"]
    if t == 1:
        # Respond to the challenge
        return {
            "statusCode": 200,
            "body": json.dumps({
                "type": 1
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    elif t == 2:
        # Handle interaction
        return handle_interaction(body, context)
    else:
        return {
            "statusCode": 400,
            "body": "Invalid request type",
            "headers": {
                "Content-Type": "application/json"
            }
        }

def handle_interaction(body, context):
    command = body["data"]["name"]
    options = body["data"].get("options", [])
    interaction_id = body["id"]
    token = body["token"]

    if command == "log":
        try:
            user_id = extract_user_id(body)
            confirmation = _log_hours_handler.handle(options, user_id)
        except ValueError as exc:
            reply(str(exc), interaction_id, token)
            return interaction_response()

        reply(confirmation, interaction_id, token)
        return interaction_response()

    if command == "display":
        try:
            result = _display_handler.handle_discord(options)
        except ValueError as exc:
            reply(str(exc), interaction_id, token, ephemeral=True)
            return interaction_response()

        reply(result.message, interaction_id, token, ephemeral=result.ephemeral)
        return interaction_response()

    reply(f"Command '{command}' is not supported yet.", interaction_id, token)
    return interaction_response()


def handle_display_event(event):
    detail = event.get("detail") or {}
    if isinstance(detail, str):
        try:
            detail = json.loads(detail)
        except json.JSONDecodeError:
            LOG.error("EventBridge detail must be valid JSON")
            return _error_response("Invalid detail payload")

    try:
        result = _display_handler.handle_event(detail)
    except ValueError as exc:
        LOG.error(f"Display event failed: {exc}")
        return _error_response(str(exc))

    LOG.info("Display event processed")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": result.message,
            "ephemeral": result.ephemeral
        }),
        "headers": {
            "Content-Type": "application/json"
        }
    }


def _is_eventbridge_event(event):
    return isinstance(event, dict) and ("detail-type" in event or event.get("source") == "aws.events")


def _error_response(message, status=400):
    return {
        "statusCode": status,
        "body": json.dumps({"error": message}),
        "headers": {
            "Content-Type": "application/json"
        }
    }


if __name__ == "__main__":
    LOG.info("DM Hours handler bootstrapped.")
