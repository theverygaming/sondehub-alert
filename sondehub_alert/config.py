import os
import json

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

SONDE_INACTIVE_SECONDS = int(os.environ["SONDE_INACTIVE_SECONDS"])

# NOTIFICATIONS format
# [
#     {
#         "lat": 1,
#         "lon": 2,
#         "radius": 50*1000,
#         "maxHeight": 3000, # won't notify if last frame's height is greater than this
#         "notify": [
#             {
#                 "platform": "telegram",
#                 "chatID": "12345678",
#             }
#         ]
#     },
# ]
NOTIFICATIONS = json.loads(os.environ["NOTIFICATIONS_CONFIG"])
