
from os import getenv
from typing import Any, AnyStr, Generator, List, Union

import firebase_admin
from firebase_admin import credentials, firestore


class FiresoreClient():

    def __init__(self, project_id: Any):
        # 初期化済みかを判定する
        if not firebase_admin._apps:

            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
        self.db = firestore.client()

    def get_collection(self, collection_name: str):
        return self.db.collection(collection_name)

    def get_document_list(self, collection_name: str):
        return self.get_collection(collection_name).stream()

    def get_document(self, collection_name: str, document_name: str):
        return self.get_collection(collection_name).document(document_name).get()

    def set_document(self, collection_name: str, document_param_id: str, obj: Any):
        collection = self.db.collection(collection_name)
        obj_dict = obj.__dict__
        # object のパラメータに動的にアクセスしたい
        doc_ref = collection.document(obj_dict[document_param_id])
        doc_ref.set(obj_dict)

    def set_document_list(self, collection_name: str, document_param_name: str,
                          object_list: Union[List, Generator]):
        collection = self.db.collection(collection_name)

        for obj in object_list:
            obj_dict = obj.__dict__
            # object のパラメータに動的にアクセスしたい
            doc_ref = collection.document(obj_dict[document_param_name])
            doc_ref.set(obj_dict)
