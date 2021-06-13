from os import getenv
import requests


def send_line(message: str):
    url = "https://notify-api.line.me/api/notify"
    token = getenv('LINE_TOKEN')
    headers = {'Authorization': 'Bearer ' + str(token)}

    payload = {'message': message}
    requests.post(url, headers=headers, params=payload,)
