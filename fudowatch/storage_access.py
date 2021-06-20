from typing import Any, Generator, List, Union

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import SERVER_TIMESTAMP


class FiresoreClient():

    def __init__(self, project_id: Any):
        # 初期化済みかを判定する
        if not firebase_admin._apps:

            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
        self.db = firestore.client()

    def set_timestamp(self, collection_name: str, document_name: str, timestamp_key: str):
        self.db.collection(collection_name).document(document_name).set({
            timestamp_key: SERVER_TIMESTAMP
        }, merge=True)

    def get_collection(self, collection_name: str):
        return self.db.collection(collection_name)

    def get_document_list(self, collection_name: str):
        return self.get_collection(collection_name).stream()

    def get_document(self, collection_name: str, document_name: str):
        return self.get_collection(collection_name).document(document_name).get()

    def set_document(self, collection_name: str, document_name: str, obj: Any, additional_timestamp_key=''):
        collection = self.db.collection(collection_name)
        obj_dict = obj.__dict__
        doc_ref = collection.document(document_name)
        doc_ref.set(obj_dict, merge=True)
        # タイムスタンプを更新
        self.set_timestamp(collection_name, document_name, 'timestamp')
        if additional_timestamp_key:
            self.set_timestamp(
                collection_name, document_name, additional_timestamp_key)

    def set_document_list(self, collection_name: str, document_name: str,
                          object_list: Union[List, Generator]):
        collection = self.db.collection(collection_name)

        for obj in object_list:
            obj_dict = obj.__dict__
            doc_ref = collection.document(document_name)
            doc_ref.set(obj_dict, merge=True)
