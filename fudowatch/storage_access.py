
from os import getenv
from typing import Generator, List, Union

import firebase_admin
from firebase_admin import credentials, firestore


class FiresoreClient():

    def __init__(self):
        # 初期化済みかを判定する
        if not firebase_admin._apps:
            project_id = getenv('GCLOUD_PROJECT')

            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
        self.db = firestore.client()

    def add_object_list(self, collection_name: str, document_param_name: str,
                        object_list: Union[List, Generator]):
        collection = self.db.collection(collection_name)

        for obj in object_list:
            obj_dict = obj.__dict__
            # object のパラメータに動的にアクセスしたい
            doc_ref = collection.document(obj_dict[document_param_name])
            doc_ref.set(obj_dict)
