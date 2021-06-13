from os import getenv

import pytest
from fudowatch.storage_access import FiresoreClient


class SampleObject():
    def __init__(self, name='name', age=1, height=1.1, adult=False, other=[1]):
        self.name = name
        self.age = age
        self.height = height
        self.adult = adult
        self.other = other


def test_storage_access():
    test_obj_list = [SampleObject(),
                     SampleObject('name2', 2, 2.2, True, [1, 2])]

    # 例外が起こらないことを確認
    try:
        client = FiresoreClient()
        client.add_object_list('test', 'name', test_obj_list)
        client.add_object_list('test/test2/test3', 'name', test_obj_list)

    except Exception:
        pytest.fail("Unexpected Exception")
