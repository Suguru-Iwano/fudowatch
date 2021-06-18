import re
from typing import Generator

from bs4 import BeautifulSoup

from fudowatch.common import get_numbers_first


# TODO:共通クラスに、以下の必須項目を記載し、継承
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
