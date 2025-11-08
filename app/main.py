import json
import os
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

try:
    from logger import Logger
    from log_hours_handler import LogHoursHandler
    from database_interface import DatabaseInterface
    from discord_utils import reply, extract_user_id, interaction_response
except ImportError:  # pragma: no cover
    from app.logger import Logger
    from app.log_hours_handler import LogHoursHandler
    from app.database_interface import DatabaseInterface
    from app.discord_utils import reply, extract_user_id, interaction_response

PUBLIC_KEY = os.getenv("PUBLIC_KEY")
_database = DatabaseInterface()
_log_hours_handler = LogHoursHandler(_database)
LOG = Logger(__file__)

def lambda_handler(event, context):
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

    reply(f"Command '{command}' is not supported yet.", interaction_id, token)
    return interaction_response()

if __name__ == "__main__":
    LOG.info("DM Hours handler bootstrapped.")
