import base64

import pytest
from main import main


def test_main():
    # 例外が起こらないことを確認
    try:
        bytes_data = b'akiyabank_nagato'
        b64encoded = base64.b64encode(bytes_data)
        main({'data': b64encoded}, None)

    except Exception as e:
        pytest.fail(str(e))
