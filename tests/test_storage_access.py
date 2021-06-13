from os import getenv
import firebase_admin
import pytest
from firebase_admin import credentials, firestore
from fudowatch.storage_access import FiresoreCrient


class TestObject():
    def __init__(self, name='name', age=1, height=1.1, adult=False, other=[1]):
        self.name = name
        self.age = age
        self.height = height
        self.adult = adult
        self.other = other


def test_storage_access():
    test_obj_list = [TestObject(),
                     TestObject('name2', 2, 2.2, True, [1, 2])]
    # 鍵の設定
    db = None
    # 以下環境変数がない場合は、ローカルと判断
    if not getenv('GCLOUD_PROJECT'):
        cred = credentials.Certificate('./tests/key/fudowatch-accesskey.json')
        firebase_admin.initialize_app(cred)
        db = firestore.client()

    # 例外が起こらないことを確認
    try:
        client = FiresoreCrient(db)
        client.add_object_list('test', 'name', test_obj_list)
        client.add_object_list('test/test2/test3', 'name', test_obj_list)

    except Exception:
        pytest.fail("Unexpected Exception")
