
from os import getenv
from typing import Generator, List, Union

import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore


class FiresoreCrient():

    def __init__(self, db=None):
        if db:
            self.db = db

        else:
            # Project ID is determined by the GCLOUD_PROJECT environment variable
            project_id = getenv('GCLOUD_PROJECT')
            cred = credentials.ApplicationDefault()

            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
            self.db = firestore.Client()

    def add_object_list(self, collection_name: str, document_param_name: str, object_list: Union[List, Generator]):
        collection = self.db.collection(collection_name)

        for obj in object_list:
            obj_dict = obj.__dict__
            # object のパラメータに動的にアクセスしたい
            doc_ref = collection.document(obj_dict[document_param_name])
            doc_ref.set(obj_dict)
