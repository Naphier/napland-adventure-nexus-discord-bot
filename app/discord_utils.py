import json
import requests


def reply(message, interaction_id, token, ephemeral: bool = False):
    url = f"https://discord.com/api/interactions/{interaction_id}/{token}/callback"

    callback_data = {
        "type": 4,
        "data": {
            "content": message
        }
    }

    if ephemeral:
        callback_data["data"]["flags"] = 64

    response = requests.post(url, json=callback_data)
    return response


def extract_user_id(body):
    member = body.get("member")
    if member and "user" in member and "id" in member["user"]:
        return member["user"]["id"]
    user = body.get("user")
    if user and "id" in user:
        return user["id"]
    raise ValueError("Unable to determine the user ID for this interaction")


def interaction_response():
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "ok"}),
        "headers": {
            "Content-Type": "application/json"
        }
    }
