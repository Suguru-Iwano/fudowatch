from typing import Generator

import pytest
from bs4 import BeautifulSoup
from fudowatch.akiyabank_nagato import (Fudosan, get_fudosan_generator,
                                        get_numbers_first, get_soup,
                                        read_config)
from main import akiyabank_nagato


def test_Fudosan():
    fudosan = Fudosan()
    # 初期値確認
    assert fudosan.name == ''
    assert fudosan.price == -1
    assert fudosan.rent == -1
    assert fudosan.parkings == 0
    assert fudosan.url_detail == ''
    assert fudosan.url_image == ''
    assert fudosan.else_data_list == []
    assert fudosan.is_published == False


def test_Fudosan_from_dict():
    d = {'name': 'name',
         'price': 1,
         # 'rent': 2,
         'parkings': 3,
         'url_detail': 'http://detail',
         # 'url_image': 'http://image',
         'else_data_list': ['one', 'two']
         }

    fudosan = Fudosan(**d)
    assert fudosan.name == 'name'
    assert fudosan.price == 1
    assert fudosan.rent == -1
    assert fudosan.parkings == 3
    assert fudosan.url_detail == 'http://detail'
    assert fudosan.url_image == ''
    assert fudosan.else_data_list == ['one', 'two']


def test_get_numbers_first():
    assert get_numbers_first('0') == 0
    assert get_numbers_first('123') == 123
    assert get_numbers_first('a123') == 123
    assert get_numbers_first('123a') == 123
    assert get_numbers_first('a123a') == 123
    assert get_numbers_first('a') == -1
    assert get_numbers_first('') == -1


def test_read_config():
    load_url = None
    # 例外が起こらないことを確認
    try:
        config_ini = read_config('config.ini')
        load_url = config_ini.get('AKIYABANK_NAGATO', 'Url')

    except Exception as e:
        pytest.fail(e.__class__.__name__ + ': ' + str(e))

    assert load_url


def test_get_soup():
    # 例外が起こらないことを確認
    try:
        get_soup('https://www.google.com/?hl=ja')

    except Exception as e:
        pytest.fail(e.__class__.__name__ + ': ' + str(e))


def test_get_fudosan_generator():
    fudosan_gen = Generator
    # 例外が起こらないことを確認
    try:
        with open('./tests/testHTML/akiyabank_nagato/akiya_itiran.html',
                  'r', encoding='utf-8') as f:
            html_str = f.read()
            soup = BeautifulSoup(html_str, "html.parser")
            fudosan_gen = get_fudosan_generator(soup)

    except Exception as e:
        pytest.fail(e.__class__.__name__ + ': ' + str(e))

    fudosan_1 = next(fudosan_gen)
    # スペースで囲まれている場合、stripされることの確認
    assert fudosan_1.name == '228 三隅中'
    assert fudosan_1.price == 1640
    assert fudosan_1.rent == 2
    assert fudosan_1.parkings == 1
    assert fudosan_1.url_detail == 'https://www.nagatoteiju.com/akiya/228'
    assert fudosan_1.url_image == 'https://www.nagatoteiju.com/cms/wp-content/uploads/IMG_5878_R.jpg'
    assert fudosan_1.else_data_list == ['庭あり']

    fudosan_2 = next(fudosan_gen)
    # ない場合（price, rent -> ×）（parkings -> なし）
    assert fudosan_2.name == '227 油谷後畑'
    assert fudosan_2.price == -1
    assert fudosan_2.rent == -1
    assert fudosan_2.parkings == 0
    assert fudosan_2.url_detail == 'https://www.nagatoteiju.com/akiya/227'
    assert fudosan_2.url_image == 'https://www.nagatoteiju.com/cms/wp-content/uploads/IMG_5732_R.jpg'
    assert fudosan_2.else_data_list == []

    fudosan_3 = next(fudosan_gen)
    # 値段範囲指定の場合
    assert fudosan_3.name == '226 油谷河原'
    assert fudosan_3.price == 1680
    assert fudosan_3.rent == 2
    assert fudosan_3.parkings == 1
    assert fudosan_3.else_data_list == ['倉庫2棟', '雑種地あり']

    fudosan_4 = next(fudosan_gen)
    # 値段0円、駐車場３台
    assert fudosan_4.name == '225 俵山湯町'
    assert fudosan_4.price == 0
    assert fudosan_4.rent == 0
    assert fudosan_4.parkings == 3

    fudosan_5 = next(fudosan_gen)
    # 駐車場のキーなし
    assert fudosan_5.name == '224 三隅上'
    assert fudosan_5.price == -1
    assert fudosan_5.rent == -1
    assert fudosan_5.parkings == 0
    assert fudosan_5.else_data_list == ['畑付き', '家財撤去済']


def test_akiyabank_nagato():
    # 例外が起こらないことを確認
    try:
        akiyabank_nagato(None, None)

    except Exception as e:
        pytest.fail(e.__class__.__name__ + ': ' + str(e))
