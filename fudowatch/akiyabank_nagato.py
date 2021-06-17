import configparser
import errno
import os
import re
import traceback
from typing import Generator

import requests
from bs4 import BeautifulSoup

from fudowatch.common import get_secret, send_line
from fudowatch.storage_access import FiresoreClient


class Fudosan():

    def __init__(self, name='', price=-1, rent=-1.0, parkings=0, url_detail='',
                 url_image='', else_data_list=[], is_posted=False):
        self.name = name
        self.price = price
        self.rent = rent
        self.parkings = parkings
        self.url_detail = url_detail
        self.url_image = url_image
        self.else_data_list = else_data_list
        self.is_posted = is_posted


def get_numbers_first(s: str) -> int:
    """最初の一塊の数字を取得する
    """
    s = s.replace(',', '')
    num_list = re.findall(r'\d+', s)
    if num_list:
        return int(num_list[0])

    else:
        return -1


def get_soup(load_url: str) -> BeautifulSoup:
    html = requests.get(load_url)
    return BeautifulSoup(html.content, 'html.parser', from_encoding='utf-8')


def get_fudosan_generator(soup: BeautifulSoup) -> Generator:
    # 空き家テーブルを取得
    table = soup.find('table', {'class': 'table_basic01'})
    # tr(行) ループ
    for tr in table.find_all('tr'):
        # 空き家情報取得
        fudosan = Fudosan()
        # １列目
        th = tr.find('th')
        col_1_a = th.find('a')
        fudosan.name = col_1_a.text.strip()
        fudosan .url_detail = col_1_a['href'].strip()
        # ２列目
        td_list = tr.find_all('td')
        col_2_a = td_list[0].find('img')
        print(col_2_a)
        fudosan.url_image = col_2_a['src'].strip()
        # ３列目
        col_3 = td_list[1]
        info_list = re.split('、|\n', col_3.text)
        info_list = [s.strip() for s in info_list]
        info_list = [s for s in info_list if s != '']  # リスト内空白を除去

        # 空き家情報をパース
        price_str = ''
        index_price = 0
        for i, s in enumerate(info_list):
            if '売買' in s:
                price_str = s
                index_price = i
                break
        if price_str:
            if '×' not in price_str:
                fudosan.price = get_numbers_first(price_str)
            del info_list[index_price]

        rent_str = ''
        index_rent = 0
        for i, s in enumerate(info_list):
            if '賃貸' in s:
                rent_str = s
                index_rent = i
                break
        if rent_str:
            if '×' not in rent_str:
                fudosan.rent = get_numbers_first(rent_str) / 10000
            del info_list[index_rent]

        # 駐車場情報の有無を確認
        # あとでリストから消して else_data_list を作りたいため、enumerate
        parking = ''
        index_parking = 0
        for i, s in enumerate(info_list):
            if '駐車場' in s:
                parking = s
                index_parking = i
                break

        if parking:
            # 駐車場が複数あるとき
            if get_numbers_first(parking) > -1:
                fudosan.parkings = get_numbers_first(parking)
            # １台のみ
            elif ('あり' in parking) or ('有' in parking):
                fudosan.parkings = 1
            del info_list[index_parking]

        else_data_list = info_list
        fudosan.else_data_list = else_data_list

        yield fudosan


def read_config(config_ini_path: str) -> configparser.ConfigParser:
    config_ini = configparser.ConfigParser()

    # 指定したiniファイルが存在しない場合、エラー発生
    if not os.path.exists(config_ini_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(
            errno.ENOENT), config_ini_path)

    config_ini.read(config_ini_path, encoding='utf-8')
    return config_ini


def akiyabank_nagato_main():
    try:
        # iniの値取得
        config_ini_path = 'config.ini'
        config_ini = read_config(config_ini_path)

        load_url = config_ini.get('AKIYABANK_NAGATO', 'Url')
        collection_name = config_ini.get('AKIYABANK_NAGATO', 'Collection')

        # Generetorにパース
        fudosan_gen = get_fudosan_generator(get_soup(load_url))

        # FireStoreのDocument一覧を取得
        project_id = os.getenv('GCLOUD_PROJECT')
        line_token = get_secret('fudowatch', 'LINE', '1')

        client = FiresoreClient(project_id)

        # documentを比較
        for f in fudosan_gen:
            # すでに登録されている情報を取得
            doc = client.get_document(collection_name, f.name)
            # すでに登録されている場合
            if doc.exists:
                pre_f = Fudosan(**doc.to_dict())
            # 登録されていない場合
            else:
                client.set_document(collection_name, 'name', f)
                send_line(line_token, f.__dict__)

    except Exception:
        print(traceback.format_exc())
        raise
