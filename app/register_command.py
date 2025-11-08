import os
import requests

try:
    from logger import Logger
except ImportError:  # pragma: no cover
    from app.logger import Logger


LOG = Logger(__file__)
APP_ID = os.getenv("APP_ID")
SERVER_ID = os.getenv("SERVER_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

LOG.info(
    f"Registering commands for app_id={APP_ID} server_id={SERVER_ID} token={BOT_TOKEN[:5]}*****"
)
# global commands are cached and only update every hour
# url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"

# while server commands update instantly
# they"re much better for testing
url = f"https://discord.com/api/v10/applications/{APP_ID}/guilds/{SERVER_ID}/commands"

json = [
  {
    "name": "log",
    "description": "Log your DM Hours",
    "options": [
        {
        'name': 'date',
        'description': 'Date of the session (YYYY-MM-DD)',
        'type': 3,  # STRING
        'required': True
      },
      {
        'name': 'hours',
        'description': 'Number of hours',
        'type': 10,  # NUMBER (float/double)
        'required': True
      },
      {
        'name': 'event',
        'description': 'Name of the session',
        'type': 3,  # STRING
        'required': True
      }
    ]
  },
  {
    "name": "display",
    "description": "Display logged DM Hours",
    "options": [
      {
        'name': 'from',
        'description': 'Start date (YYYY-MM-DD)',
        'type': 3,
        'required': False
      },
      {
        'name': 'to',
        'description': 'End date (YYYY-MM-DD)',
        'type': 3,
        'required': False
      },
      {
        'name': 'discord_name',
        'description': 'Filter results by Discord username',
        'type': 3,
        'required': False
      }
    ]
  }
]

response = requests.put(
    url, headers={
  "Authorization": f"Bot {BOT_TOKEN}"
}, json=json)

LOG.info(f"Discord response: {response.json()}")
