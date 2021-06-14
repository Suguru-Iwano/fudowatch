import pytest
from fudowatch.common import send_line


def test_send_line():
    # 例外が起こらないことを確認
    try:
        res = send_line(message='Write Your Message')
        assert res.status_code == 200

    except Exception:
        pytest.fail("Unexpected Exception")
