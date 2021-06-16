
import pytest
from fudowatch.common import get_secret, send_line


def test_get_secret():
    secret_str = None
    # 例外が起こらないことを確認
    try:
        secret_str = get_secret('fudowatch', 'TEST', '1')

    except Exception as e:
        pytest.fail(e.__class__.__name__ + ': ' + str(e))

    assert secret_str == 'Able to get secret.'


def test_send_line():
    res = None
    token = get_secret('fudowatch', 'LINE', '1')
    # 例外が起こらないことを確認
    try:
        res = send_line(token, 'Write Your Message')

    except Exception as e:
        pytest.fail(e.__class__.__name__ + ': ' + str(e))

    assert res.status_code == 200
