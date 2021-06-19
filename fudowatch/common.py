import base64
import configparser
import errno
import os
import re

import requests
from bs4 import BeautifulSoup
from google.cloud import secretmanager
from requests.models import Response


def get_pubsub_message(event) -> str:
    if 'data' in event:
        return base64.b64decode(event['data']).decode('utf-8')
    else:
        return ''


def read_config(config_ini_path: str) -> configparser.ConfigParser:
    config_ini = configparser.ConfigParser()

    # 指定したiniファイルが存在しない場合、エラー発生
    if not os.path.exists(config_ini_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(
            errno.ENOENT), config_ini_path)

    config_ini.read(config_ini_path, encoding='utf-8')
    return config_ini


def get_soup(load_url: str) -> BeautifulSoup:
    html = requests.get(load_url)
    if html.status_code != 200:
        raise ValueError
    return BeautifulSoup(html.content, 'html.parser', from_encoding='utf-8')


def get_numbers_first(s: str) -> int:
    """最初の一塊の数字を取得する
    """
    s = s.replace(',', '')
    num_list = re.findall(r'\d+', s)
    if num_list:
        return int(num_list[0])

    else:
        return -1


def get_secret(project_id: str, secret_name: str, secret_ver: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_name, secret_ver)
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")


def send_message(token: str, message: str) -> Response:
    url = "https://notify-api.line.me/api/notify"
    headers = {'Authorization': 'Bearer ' + str(token)}

    payload = {'message': message}
    return requests.post(url, headers=headers, params=payload,)
