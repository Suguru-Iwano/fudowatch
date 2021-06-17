
import os

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
    test_obj = SampleObject()
    test_obj_list = [SampleObject(),
                     SampleObject('name2', 2, 2.2, True, [1, 2])]
    project_id = os.getenv('GCLOUD_PROJECT')
    # 例外が起こらないことを確認
    try:
        client = FiresoreClient(project_id)
        client.set_document(
            'test/storage_access/set_document', 'name', test_obj)
        client.set_document_list(
            'test/storage_access/set_document_list', 'name', test_obj_list)

    except Exception as e:
        pytest.fail(e.__class__.__name__ + ': ' + str(e))
