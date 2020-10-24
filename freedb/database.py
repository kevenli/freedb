from enum import Enum
import logging
import os
import re

from bson import ObjectId
from django.conf import settings
from pymongo import MongoClient
import pymongo.errors
from pymongo.collection import Collection

from .utils import snowflake

#from mongoengine import connect
#mongodb_url = os.environ.get('MONGODB_URL', 'mongomock://localhost')
#connect("ddmongo", host=mongodb_url, alias="default")


logger = logging.getLogger(__name__)


client = MongoClient(settings.MONGODB_URL)


id_generator = snowflake.generator(1,1)


def next_ts():
    return next(id_generator)


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


def iter_doc_items(doc, skip__id=True):
    """
    iter field_name: field_value over posted doc.
    make some data check and regularizations:
        1. field name must not be start with underscore(_) and be valid to a python variable name.
        2. field name will not be longger that 64 characters.
        3. convert field to lower case, so that the field_name will not be case-sensitive
        4. convert field_value according schema settings.(will implement in the future)
    """
    field_name_pattern = '[a-zA-Z][\w_]{0,63}'
    for field_name, field_value in doc.items():
        if field_name == '_id':
            if skip__id:
                continue
            yield field_name, field_value
        elif not re.match(field_name_pattern, field_name):
            raise Exception('Invalid field name. %s' % field_name)

        field_name = field_name.lower()
        yield field_name, field_value


def save_item(col, doc, id_field=None, existing_policy: ExistingRowPolicy = ExistingRowPolicy.Skip):
    if len(doc) == 0:
        raise Exception("Post data cannot be null.")
    
    if id_field:
        doc_id = doc.get(id_field)
    else:
        doc_id = doc.get('id')
    
    if doc_id:
        if not isinstance(doc_id, (str, ObjectId)):
            doc_id = str(doc_id)
        doc['_id'] = doc_id

    #if doc_id and not isinstance(doc_id, ObjectId):
    #    doc['_id'] = str(doc_id)

    existing = None 
    if doc_id:
        existing = col.find_one({'_id': doc_id})

    if existing:
        if existing_policy == ExistingRowPolicy.Skip:
            return doc_id, 'skipped'
        
        if existing_policy == ExistingRowPolicy.Merge:
            # for k, v in doc.items():
            #     existing[k] = v
            # existing['_ts'] = next_ts()
            update_object = {}
            changed = False
            doc_id = doc.pop('id', None) or doc_id 
            for field_name, field_value in iter_doc_items(doc):
                if field_name == 'id':
                    continue
                update_object[field_name] = field_value
                logger.debug('Comparing field values: %s: old: %s, new: %s', 
                             field_name, 
                             existing.get(field_name), 
                             field_value)
                if field_value != existing.get(field_name):
                    changed = True

            if changed:
                update_object['_ts'] = next_ts()
                return col.update(doc_id, update_object), 'merged'
            else:
                return existing['id'], 'merged'

        if existing_policy == ExistingRowPolicy.Overwrite:
            doc = {key.lower(): value for key, value in doc.items()}
            doc['_ts'] = next_ts()
            
            #col.update_one({'_id': doc_id}, doc)
            return col.save_overwrite(doc), 'overwroten'

    
    else:
        doc = {key.lower(): value for key, value in doc.items()}
        doc['_ts'] = next_ts()
        try:
            new_id = col.insert_one(doc).inserted_id
            return new_id, 'created'
        except pymongo.errors.DuplicateKeyError:
            return doc['_id'], 'skipped'


class DataCollection:
    """
    A proxy to make operations to the underlying mongo collection 
    with some additional options.
    """

    def __init__(self, underlying: Collection):
        self.underlying = underlying

    def get(self, doc_id):
        try:
            doc_id = ObjectId(doc_id)
        except:
            pass

        return self.underlying.find_one({'_id': doc_id})

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

    def update(self, doc_id: str, update_doc: dict):
        try:
            doc_id = ObjectId(doc_id)
        except:
            pass

        update_ret = self.underlying.update_one({'_id': doc_id}, {'$set': update_doc})
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

    def find_one_and_delete(self, filter):
        return self.underlying.find_one_and_delete(filter=filter)

    def find_one_and_update(self, filter, doc):
        return self.underlying.find_one_and_update(filter=filter, update=doc)

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
