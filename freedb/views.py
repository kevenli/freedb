import base64
from enum import Enum
import json
import logging
import os
from django.shortcuts import render
from django.views.generic import ListView
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
import django.db.utils
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from bson.json_util import dumps
from bson import ObjectId
from bson.errors import InvalidId
import pymongo
from .models import Database, Collection
from . import models
from .database import get_db_collection, client, ExistingRowPolicy, next_ts
from .serializers import DatabaseSerializer


logger = logging.getLogger(__name__)


def serialize_doc(doc):
    # doc['_id'] = str(doc['_id'])
    doc['id'] = str(doc.pop('_id'))
    return dict(doc)
    return doc


class IndexView(LoginRequiredMixin, ListView):
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
        if not db_name:
            return Response(data={
                'err_msg': 'db_name cannot be null'
            },status=400)

        try:
            database = Database(owner=request.user, name=db_name)
            database.save()
        except django.db.utils.IntegrityError:
            return Response(data={
                'err_msg': 'db already exists'
            }, status=409)

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
        try:
            collection.save()
        except django.db.utils.IntegrityError:
            return Response(status=409, data={
                'err_msg': 'collection already exists.'
            })

        actual_col_name = collection_name + '_' + str(collection.id)
        mongo_db = client[database.name]
        mongo_col = mongo_db[actual_col_name]

        collection.actual_col_name = actual_col_name
        collection.save()

        return JsonResponse({})


class DatabaseCollectionInstance(APIView):
    def get(self, request, db_name, col_name):
        try:
            database = models.Database.objects.get(owner=request.user, name=db_name)
        except models.Database.DoesNotExist:
            return Response(status=404)
        try:
            collection = models.Collection.objects.get(database=database, name=col_name)
        except models.Collection.DoesNotExist:
            return Response(status=404)
        mongo_col = get_db_collection(collection)
        query = json.loads(request.GET.get('query', '{}'))
        if 'id' in query:
            try:
                query["_id"] = ObjectId(query["id"])
            except:
                query['_id'] = str(query["id"])
            finally:
                query.pop('id')

        limit = int(request.GET.get('limit', 20))
        skip = int(request.GET.get('skip', 0))
        try:
            param_sort = json.loads(request.GET.get('sort', '{}'))
        except json.decoder.JSONDecodeError:
            param_sort = {}
        sort = list(param_sort.items())
        query_count = mongo_col.count_documents(query)
        paging = {
            'limit': limit,
            'skip': skip,
            'total': query_count
        }

        docs = []
        rows_count = 0
        for doc in mongo_col.find(filter=query, limit=limit, skip=skip, sort=sort):
            docs.append(serialize_doc(doc))
            rows_count += 1
        paging['rows'] = rows_count
        return Response({
            "data": docs,
            'paging': paging
        })


class DatabaseIndex(LoginRequiredMixin, ListView):
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
        limit = int(request.GET.get('limit', 20))
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


class JsonLineItemStream:
    def __init__(self, filepath):
        self.f = open(filepath, 'r')

    def __iter__(self):
        return self

    def __next__(self):
        line  = next(self.f)
        return json.loads(line)


def save_item(col, doc, id_field=None, existing_policy: ExistingRowPolicy = ExistingRowPolicy.Skip):
    if len(doc) == 0:
        raise Exception("Post data cannot be null.")
    
    if id_field:
        doc_id = doc.get(id_field)
    else:
        doc_id = doc.get('id')
    
    if doc_id is not None:
        doc['_id'] = str(doc_id)

    existing = None 
    if doc_id:
        existing = col.find_one({'_id': doc_id})

    if existing:
        if existing_policy == ExistingRowPolicy.Skip:
            return doc_id, 'skipped'
        
        if existing_policy == ExistingRowPolicy.Merge:
            for k, v in doc.items():
                existing[k] = v
            existing['_ts'] = next_ts()

            return col.merge(existing), 'merged'

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
            return str(new_id), 'created'
        except pymongo.errors.DuplicateKeyError:
            return str(doc['_id']), 'skipped'


class DatabaseCollectionDocuments(APIView):
    def post(self, request, db_name, col_name):
        try:
            database = models.Database.objects.get(owner=self.request.user, name=db_name)
            collection = models.Collection.objects.get(database=database, name=col_name)
            col = get_db_collection(collection)
        except models.Database.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Database not found.'}, status=400, reason='Database not found.')
        except models.Collection.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Collection not found.'}, status=400, reason='Collection not found.')

        existing_policy = ExistingRowPolicy.from_str(request.GET.get('exist')) or ExistingRowPolicy.Skip
        item = request.data
        saved_id, result = save_item(col, item, existing_policy=existing_policy)
        try:
            saved_id = ObjectId(saved_id)
        except:
            pass
        saved_doc = col.find_one({'_id': saved_id})
        return Response(serialize_doc(saved_doc))

    def delete(self, request, db_name, col_name):
        """
        Truncate the collection documents.
        """
        try:
            database = models.Database.objects.get(owner=self.request.user, name=db_name)
            collection = models.Collection.objects.get(database=database, name=col_name)
            col = get_db_collection(collection)
        except models.Database.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Database not found.'}, status=400, reason='Database not found.')
        except models.Collection.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Collection not found.'}, status=400, reason='Collection not found.')

        col.truncate()
        return Response()

    def get(self, request, db_name, col_name):
        try:
            database = models.Database.objects.get(owner=self.request.user, name=db_name)
            collection = models.Collection.objects.get(database=database, name=col_name)
            col = get_db_collection(collection)
        except models.Database.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Database not found.'}, status=400, reason='Database not found.')
        except models.Collection.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Collection not found.'}, status=400, reason='Collection not found.')

        mongo_col = col
        query = json.loads(request.GET.get('query', '{}'))
        if 'id' in query:
            try:
                query["_id"] = ObjectId(query["id"])
            except:
                query['_id'] = str(query["id"])
            finally:
                query.pop('id')

        limit = int(request.GET.get('limit', 20))
        skip = int(request.GET.get('skip', 0))
        try:
            param_sort = json.loads(request.GET.get('sort', '{}'))
        except json.decoder.JSONDecodeError:
            param_sort = {}
        sort = list(param_sort.items())
        query_count = mongo_col.count_documents(query)
        paging = {
            'limit': limit,
            'skip': skip,
            'total': query_count
        }

        docs = []
        rows_count = 0
        for doc in mongo_col.find(filter=query, limit=limit, skip=skip, sort=sort):
            docs.append(serialize_doc(doc))
            rows_count += 1
        paging['rows'] = rows_count
        return Response({
            "data": docs,
            'paging': paging
        })


class DatabaseCollectionDocumentsBatchSave(APIView):
    def post(self, request, db_name, col_name):
        try:
            database = models.Database.objects.get(owner=self.request.user, name=db_name)
            collection = models.Collection.objects.get(database=database, name=col_name)
            col = get_db_collection(collection)
        except models.Database.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Database not found.'}, status=400, reason='Database not found.')
        except models.Collection.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Collection not found.'}, status=400, reason='Collection not found.')

        exist_policy = request.GET.get('exist', 'skip')
        """
        exist policies:
            skip: if the specified id exists, skip current row and return the existing id.
            update: compare and update modified fields
            overwrite: overwrite the record with the uploading one.
        """

        existing_policy = ExistingRowPolicy.from_str(request.GET.get('exist')) or ExistingRowPolicy.Skip

        stream = None
        if 'file' in request.FILES:
            upload_file = request.FILES['file']
            upload_ext = os.path.splitext(upload_file.name)[-1]
            if upload_ext.lower() == '.jl':
                # json line file
                stream = JsonLineItemStream(upload_file.temporary_file_path())
            else:
                stream = [json.loads(upload_file.read())]
        else:
            stream = request.data

        ret = []
        for item in stream:
            saved_id, result = save_item(col, item, existing_policy=existing_policy)
            ret.append({
                "id": saved_id,
                'result': result
            })

        return Response(ret)


class DatabaseCollectionDocumentsImport(APIView):
    def post(self, request, db_name, col_name):
        try:
            database = models.Database.objects.get(owner=self.request.user, name=db_name)
            collection = models.Collection.objects.get(database=database, name=col_name)
            col = get_db_collection(collection)
        except models.Database.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Database not found.'}, status=400, reason='Database not found.')
        except models.Collection.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Collection not found.'}, status=400, reason='Collection not found.')

        existing_policy = ExistingRowPolicy.from_str(request.GET.get('exist')) or ExistingRowPolicy.Skip

        stream = None
        if 'file' not in request.FILES:
            return JsonResponse(data={'errmsg': 'Not import file found.'}, status=400, reason='Collection not found.')

        id_field = request.GET.get('id_field')

        upload_file = request.FILES['file']
        upload_ext = os.path.splitext(upload_file.name)[-1]
        if upload_ext.lower() == '.jl':
            # json line file
            stream = JsonLineItemStream(upload_file.temporary_file_path())
        else:
            stream = [json.loads(upload_file.read())]

        ret = []
        for item in stream:
            saved_id, result = save_item(col, item, id_field=id_field, existing_policy=existing_policy)
            ret.append({
                "id": saved_id,
                'result': result
            })

        return Response(ret)


class DatabaseCollectionDocumentsSync(APIView):
    def get(self, request, db_name, col_name):
        try:
            database = models.Database.objects.get(owner=self.request.user, name=db_name)
            collection = models.Collection.objects.get(database=database, name=col_name)
            mongo_col = get_db_collection(collection)
        except models.Database.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Database not found.'}, status=400, reason='Database not found.')
        except models.Collection.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Collection not found.'}, status=400, reason='Collection not found.')
        
        limit = int(request.GET.get('limit', 20))
        if limit > 100:
            limit = 100

        page_token = request.GET.get('page_token')

        last_ts = None
        query = {
            '_ts': {
                "$exists": True
            }
        }
        if page_token:
            last_ts = int(base64.b64decode(page_token).decode())
            query['_ts']['$gt'] = last_ts

        docs = []
        rows_count = 0
        sort = [('_ts', 1)]
        for doc in mongo_col.find(filter=query, limit=limit, sort=sort):
            docs.append(serialize_doc(doc))
            rows_count += 1
        
        next_page_token = None
        if docs:
            next_page_token = base64.b64encode(str(docs[-1]['_ts']).encode()).decode()

        return Response({
            "docs": docs,
            'next_page_token': next_page_token or page_token
        })


class DatabaseCollectionDocumentInstance(APIView):
    def get(self, request, db_name, col_name, doc_id):
        try:
            database = models.Database.objects.get(owner=self.request.user, name=db_name)
            collection = models.Collection.objects.get(database=database, name=col_name)
            col = get_db_collection(collection)
        except models.Database.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Database not found.'}, status=400, reason='Database not found.')
        except models.Collection.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Collection not found.'}, status=400, reason='Collection not found.')

        try:
            doc_id = ObjectId(doc_id)
        except:
            pass
        doc = col.find_one({"_id": doc_id})
        if not doc:
            return Response(status=404)
        doc['id'] = str(doc.pop('_id'))
        return Response(doc)

    def delete(self, request, db_name, col_name, doc_id):
        try:
            database = models.Database.objects.get(owner=self.request.user, name=db_name)
            collection = models.Collection.objects.get(database=database, name=col_name)
            col = get_db_collection(collection)
        except models.Database.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Database not found.'}, status=400, reason='Database not found.')
        except models.Collection.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Collection not found.'}, status=400, reason='Collection not found.')
        try:
            doc_id = ObjectId(doc_id)
        except:
            pass

        doc = col.get(doc_id)
        if not doc:
            return JsonResponse(data={'errmsg': 'Document not found.'}, status=404, reason='Document not found.')

        result = col.delete_one({"_id": doc_id})
        return Response()


class DatabaseCollectionFieldsView(APIView):
    def put(self, request, db_name, col_name):
        try:
            database = models.Database.objects.get(owner=self.request.user, name=db_name)
            collection = models.Collection.objects.get(database=database, name=col_name)
            col = get_db_collection(collection)
        except models.Database.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Database not found.'}, status=400, reason='Database not found.')
        except models.Collection.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Collection not found.'}, status=400, reason='Collection not found.')

        fields = request.data

        with transaction.atomic():
            models.Field.objects.filter(collection=collection).delete()

            for i, field in enumerate(fields):
                field_model = models.Field(collection=collection, 
                                           field_name=field['name'], 
                                           field_type=field['type'],
                                           sort_no=i)
                field_model.save()
            
        saved_fields = [{
            "name": f.field_name,
            'type': f.field_type,
        } for f in models.Field.objects.filter(collection=collection).order_by('sort_no')]
        return JsonResponse(data=saved_fields, safe=False)

    def get(self, request, db_name, col_name):
        try:
            database = models.Database.objects.get(owner=self.request.user, name=db_name)
            collection = models.Collection.objects.get(database=database, name=col_name)
            col = get_db_collection(collection)
        except models.Database.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Database not found.'}, status=400, reason='Database not found.')
        except models.Collection.DoesNotExist:
            return JsonResponse(data={'errmsg': 'Collection not found.'}, status=400, reason='Collection not found.')

        saved_fields = [{
            "name": f.field_name,
            'type': f.field_type,
        } for f in models.Field.objects.filter(collection=collection).order_by('sort_no')]
        return JsonResponse(data=saved_fields, safe=False)
