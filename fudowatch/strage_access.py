
from google.cloud import firestore


def get_db(collection_name: str, document_name: str):
    # Project ID is determined by the GCLOUD_PROJECT environment variable
    db = firestore.Client()

    doc_ref = db.collection(collection_name).document(document_name)
    doc_ref.set({
        u'first': u'Ada',
        u'last': u'Lovelace',
        u'born': 1815
    })
