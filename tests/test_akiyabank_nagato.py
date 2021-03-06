from typing import Generator

import pytest
from bs4 import BeautifulSoup
from fudowatch.akiyabank_nagato import get_fudosan_generator


def test_get_fudosan_generator():
    fudosan_gen = Generator
    # 例外が起こらないことを確認
    try:
        with open('./tests/html/akiyabank_nagato/akiya_itiran.html',
                  'r', encoding='utf-8') as f:
            html_str = f.read()
            soup = BeautifulSoup(html_str, "html.parser")
            fudosan_gen = get_fudosan_generator(soup)

    except Exception as e:
        pytest.fail(str(e))

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
