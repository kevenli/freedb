import os
from django.conf import settings
from pymongo import MongoClient
from pymongo.collection import Collection

#from mongoengine import connect
#mongodb_url = os.environ.get('MONGODB_URL', 'mongomock://localhost')
#connect("ddmongo", host=mongodb_url, alias="default")

client = MongoClient(settings.MONGODB_URL)

def get_db_collection(collection) -> Collection:
    #client = MongoClient('mongomock://localhost')
    #client = connect("ddmongo", host=mongodb_url, alias="default")
    db = client[collection.database.name]
    col = db[collection.name]
    return col