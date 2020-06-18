import json
import logging
from django.shortcuts import render
from django.views.generic import ListView
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from bson.json_util import dumps
from bson import ObjectId
from bson.errors import InvalidId
import pymongo
from .models import Database, Collection
from .database import get_db_collection, client
from .serializers import DatabaseSerializer


logger = logging.getLogger(__name__)


def serialize_doc(doc):
    # doc['_id'] = str(doc['_id'])
    doc['id'] = str(doc.pop('_id'))
    return dict(doc)
    return doc

# Create your views here.
class IndexView(ListView):
    model = Database
    template_name = 'freedb/index.html'

    def get_queryset(self):
        return Database.objects.filter(owner=self.request.user)


class DatabaseList(APIView):
    def get(self, request):
        databases = Database.objects.filter(owner=self.request.user).all()
        #return Response(databases)
        serializer = DatabaseSerializer(databases, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        db_name = request.data.get('name')
        database = Database(owner=request.user, name=db_name)
        database.save()

        mongo_database = client[database.name]
        dblist = client.list_database_names()
        logger.debug(dblist)

        return JsonResponse({"name": db_name})


class DatabaseInstance(APIView):
    @transaction.atomic
    def delete(self, request, db_name):
        database = Database.objects.get(owner=request.user, name=db_name)
        database.delete()
        client.drop_database(db_name)
        return JsonResponse({})

    def get(self, request, db_name):
        database = Database.objects.get(owner=request.user, name=db_name)
        collections = Collection.objects.filter(database=database)

        return JsonResponse({
            "name": database.name,
            'collections': [
                {"name": x.name} for x in collections
            ]
        })


class DatabaseCollectionList(APIView):
    @transaction.atomic
    def post(self, request, db_name):
        database = Database.objects.get(owner=request.user, name=db_name)
        collection_name = self.request.data.get('name')
        collection = Collection(database=database, name=collection_name)
        collection.save()

        mongo_db = client[database.name]
        mongo_col = mongo_db[collection.name]

        return JsonResponse({})


class DatabaseCollectionInstance(APIView):
    def get(self, request, db_name, col_name):
        database = Database.objects.get(owner=request.user, name=db_name)
        collection = Collection.objects.get(database=database, name=col_name)
        mongo_col = get_db_collection(collection)
        query = request.GET.get('query', '{}')
        docs = []
        for doc in mongo_col.find():
            docs.append(serialize_doc(doc))
        return Response(docs)


class DatabaseIndex(ListView):
    model = Collection
    template_name = 'freedb/database_index.html'

    def get_queryset(self):
        db_name = self.kwargs.get('database_name')
        db = Database.objects.get(owner=self.request.user, name=db_name)
        return Collection.objects.filter(database=db)


class CollectionView(APIView):
    # def __init__(self, database_name, collection_name):
    #     self.database_name = database_name
    #     self.collection_name = collection_name
    def _get_col(self, database_name, collection_name):
        database = Database.objects.get(owner=self.request.user, name=database_name)
        collection = Collection.objects.get(database=database, name=collection_name)
        col = get_db_collection(collection)
        return col

    def get(self, request, database_name=None, collection_name=None):
        database = Database.objects.get(owner=self.request.user, name=database_name)
        collection = Collection.objects.get(database=database, name=collection_name)
        accept = request.META.get('HTTP_ACCEPT', 'text/html')

        col = get_db_collection(collection)
        #col.

        if 'text/html' in accept:
            return render(request, 'freedb/collection_view.html')

        query = json.loads(request.GET.get('query', '{}'))
        #docs = col.find(query)

        docs = []
        for doc in col.find():
            docs.append(serialize_doc(doc))
        return Response(dumps(docs))


    def post(self, request, database_name=None, collection_name=None):
        docs = [request.data]
        # if not (isinstance(docs, list) and len(docs) == 1):
        #     docs = [docs]
        col = self._get_col(database_name, collection_name)
        ret = []
        for doc in docs:
            if 'id' in doc:
                doc['_id'] = str(doc['id'])
            try:
                new_id = col.insert_one(doc).inserted_id
                ret.append({"id": str(new_id), 'status':'created'})
            except pymongo.errors.DuplicateKeyError:
                ret.append({"id": doc['id'], 'status': 'skipped'})
        return Response(ret)


class CollectionRowView(APIView):
    def _get_col(self, database_name, collection_name):
        database = Database.objects.get(owner=self.request.user, name=database_name)
        collection = Collection.objects.get(database=database, name=collection_name)
        col = get_db_collection(collection)
        return col

    def get(self, request, database_name, collection_name, row_id):
        col = self._get_col(database_name, collection_name)
        row = col.find_one({"_id": row_id})
        if not row:
            return Response({})
        return Response(serialize_doc(row))

    def delete(self, request, database_name, collection_name, row_id):
        col = self._get_col(database_name, collection_name)
        row = col.find_one_and_delete({"_id": row_id})
        return Response({})

    def put(self, request, database_name, collection_name, row_id):
        col = self._get_col(database_name, collection_name)
        new_row = self.request.data
        try:
            row_id = ObjectId(row_id)
        except InvalidId:
            row_id = str(row_id)
        row = col.find_one_and_update({"_id": row_id}, new_row)
        return Response({})