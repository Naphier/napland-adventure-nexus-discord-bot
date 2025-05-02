import requests
import os


APP_ID = os.getenv("APP_ID")
SERVER_ID = os.getenv("SERVER_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

print(APP_ID, SERVER_ID, BOT_TOKEN[:5] + "*****")
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
  }
]

response = requests.put(url, headers={
  "Authorization": f"Bot {BOT_TOKEN}"
}, json=json)

print(response.json())