from enum import Enum
import os
from django.conf import settings
from pymongo import MongoClient
from pymongo.collection import Collection

#from mongoengine import connect
#mongodb_url = os.environ.get('MONGODB_URL', 'mongomock://localhost')
#connect("ddmongo", host=mongodb_url, alias="default")

client = MongoClient(settings.MONGODB_URL)


class ExistingRowPolicy(Enum):
    Skip = 0,
    Merge = 1,
    Overwrite = 2

    @classmethod
    def from_str(cls, s, raise_error=False):
        if s == 'skip':
            return ExistingRowPolicy.Skip
        elif s == 'merge':
            return ExistingRowPolicy.Merge
        elif s == 'overwrite':
            return ExistingRowPolicy.Overwrite
        elif raise_error:
            raise Exception(f'Not supported ExistingRowPolicy: {s}')
        else:
            return None


class DataCollection:
    """
    A proxy to make operations to the underlying mongo collection 
    with some additional options.
    """

    def __init__(self, underlying: Collection):
        self.underlying = underlying

    def find_one(self, filter=None, *args, **kwargs):
        return self.underlying.find_one(filter, *args, **kwargs)

    def update_one(self, filter, update, *args, **kwargs):
        return self.underlying.update_one(filter, update, *args, **kwargs)

    def insert_one(self, document, **kwargs):
        return self.underlying.insert_one(document, **kwargs)

    def delete_one(self, filter, **kwargs):
        return self.underlying.delete_one(filter, **kwargs)

    def truncate(self):
        return self.underlying.remove()

    def count_documents(self, query, **kwargs):
        return self.underlying.count_documents(query, **kwargs)

    def find(self, *args, **kwargs):
        return self.underlying.find(*args, **kwargs)

    def merge(self, doc):
        doc_id = doc.pop('id', None)
        doc__id = doc.pop('_id', None)
        try:
            doc_id = ObjectId(doc_id)
        except:
            pass
        update_ret = self.underlying.update_one({'_id': doc_id}, {'$set': doc}, upsert=True)
        return update_ret.upserted_id or doc_id

    def save_overwrite(self, doc):
        doc_id = doc.pop('id', None)
        doc__id = doc.pop('_id', None)
        try:
            doc_id = ObjectId(doc_id)
        except:
            pass
        update_ret = self.underlying.replace_one({'_id': doc_id}, doc, upsert=True)
        return update_ret.upserted_id or doc_id

def get_db_collection(collection) -> DataCollection:
    #client = MongoClient('mongomock://localhost')
    #client = connect("ddmongo", host=mongodb_url, alias="default")
    db = client.db
    actual_col_name = collection.actual_col_name or collection.name
    col = db[actual_col_name]
    if not collection.actual_col_name:
        collection.actual_col_name = actual_col_name
        collection.save()

    return DataCollection(col)
