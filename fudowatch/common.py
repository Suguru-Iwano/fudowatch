from os import getenv

import requests
from requests.models import Response


def send_line(message: str) -> Response:
    url = "https://notify-api.line.me/api/notify"
    token = getenv('LINE_TOKEN')
    headers = {'Authorization': 'Bearer ' + str(token)}

    payload = {'message': message}
    return requests.post(url, headers=headers, params=payload,)
