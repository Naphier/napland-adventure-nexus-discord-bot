import json
import os
import requests
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

PUBLIC_KEY = os.getenv("PUBLIC_KEY")

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
    
    t == body["type"]
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

def reply(message, id, token):
    url = f"https://discord.com/api/interactions/{id}/{token}/callback"

    callback_data = {
        "type": 4,
        "data": {
            "content": message
        }
    }
    response = requests.post(url, json=callback_data)