import requests
from google.cloud import secretmanager
from requests.models import Response


def get_secret(project_id: str, secret_name: str, secret_ver: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_name, secret_ver)
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")


def send_line(token: str, message: str) -> Response:
    url = "https://notify-api.line.me/api/notify"
    headers = {'Authorization': 'Bearer ' + str(token)}

    payload = {'message': message}
    return requests.post(url, headers=headers, params=payload,)
