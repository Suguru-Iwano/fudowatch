import pytest
from fudowatch.common import (get_numbers_first, get_secret, get_soup,
                              read_config, send_message)


def test_get_soup():
    # 例外が起こらないことを確認
    try:
        get_soup('https://www.google.com/?hl=ja')

    except Exception as e:
        pytest.fail(e.__class__.__name__ + ': ' + str(e))


def test_read_config():
    config_ini = read_config('./tests/config/test_config.ini')
    assert config_ini.get('TEST', 'Url') == 'testurl'


def test_get_numbers_first():
    assert get_numbers_first('0') == 0
    assert get_numbers_first('123') == 123
    assert get_numbers_first('a123') == 123
    assert get_numbers_first('123a') == 123
    assert get_numbers_first('a123a') == 123
    assert get_numbers_first('a') == -1
    assert get_numbers_first('') == -1


def test_read_config_error():
    with pytest.raises(FileNotFoundError):
        read_config('./dummyfile.ini')


def test_get_secret():
    secret_str = None
    # 例外が起こらないことを確認
    try:
        secret_str = get_secret('fudowatch', 'TEST', '1')

    except Exception as e:
        pytest.fail(e.__class__.__name__ + ': ' + str(e))

    assert secret_str == 'Able to get secret.'


def test_send_message():
    res = None
    token = get_secret('fudowatch', 'LINE', '1')
    # 例外が起こらないことを確認
    try:
        res = send_message(token, 'Test')

    except Exception as e:
        pytest.fail(e.__class__.__name__ + ': ' + str(e))

    assert res.status_code == 200
