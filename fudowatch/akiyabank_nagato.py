import configparser
import errno
import os
import re
import traceback
from typing import Generator

import requests
from bs4 import BeautifulSoup

from fudowatch.common import get_secret, send_message
from fudowatch.storage_access import FiresoreClient


class Fudosan():

    def __init__(self, id='', name='', price=-1, rent=-1.0, parkings=0, url_detail='',
                 url_image='', else_data_list=[], is_published=True):
        self.id = id  # 必須
        self.name = name  # 必須
        self.price = price  # 必須
        self.rent = rent
        self.parkings = parkings  # 必須
        self.url_detail = url_detail  # 必須
        self.url_image = url_image
        self.else_data_list = else_data_list
        self.is_published = is_published  # 必須


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
        fudosan.id = fudosan.name = col_1_a.text.strip()
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
        fudosan.is_published = True

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

        project_id = os.getenv('GCLOUD_PROJECT')
        line_token = get_secret('fudowatch', 'LINE', '1')

        client = FiresoreClient(project_id)
        # 物件情報を取得
        fudosan_collection = client.get_collection(collection_name)

        # 公開されている物件情報を取得しておく（fudosan_genにないものをFalseしたい）
        doc_is_pub = fudosan_collection.where(
            u'is_published', u'==', True)

        published_id_list = []

        for f in fudosan_gen:
            # すでに登録されている情報を取得
            pre_f = fudosan_collection.document(f.id).get()
            # 公開物件リストに登録
            published_id_list.append(pre_f.id)
            # すでに登録されている場合
            if pre_f.exists:
                # 変更がある場合
                if pre_f._data != f.__dict__:
                    pre_f_obj = Fudosan(**pre_f.to_dict())
                    # 登録

            # 登録されていない場合
            else:
                client.set_document(collection_name, 'id', f)
                message = f"""
新しい物件情報があります。
物件名: {f.name}
売値: 　{f.price}万円
{f.url_detail}"""
                send_message(line_token, message)

        # 非公開になった物件を更新
        for f in doc_is_pub.stream():
            if f.id not in published_id_list:
                fudosan_collection.document(
                    f.id).update({'is_published': False})

    except Exception:
        print(traceback.format_exc())
        raise
