import json
import os

from django.test import TestCase
from django.contrib.auth import get_user_model
import django.contrib.auth
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from freedb.models import Database, Collection
User = get_user_model()


class ApiTest(TestCase):
    def setUp(self):
        super().setUp()
        User = get_user_model()
        tester, _= User.objects.get_or_create(username='tester')
        tester.save()
        self.user = tester

        token, _ = Token.objects.get_or_create(user=tester)
        token.save()
        self.token = token

    def build_api_collection_documents_url(self, collection):
        return f'/api/databases/{collection.database.name}/collections/{collection.name}/documents'
                    
    def try_create_collection(self, db_name, col_name):
        db, _ = Database.objects.get_or_create(name=db_name, owner=self.user)
        db.save()

        col, _ = Collection.objects.get_or_create(name=col_name, database=db)
        col.save()
        return col

    def test_query_docs(self):
        collection = self.try_create_collection('testdb', 'testcol')

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        docs = []
        with open(os.path.join(os.path.dirname(__file__), 'example.jl')) as f:
            for line in f.readlines():
                doc = json.loads(line)
                docs.append(doc)

        for doc in docs:
            client.post(self.build_api_collection_documents_url(collection), data=doc, format='json')

        response = client.get(self.build_api_collection_documents_url(collection))
        response_data = json.loads(response.content)['data']
        def remove_system_fields(doc):
            doc.pop('_ts')
            return doc
        
        self.assertEqual(3, len(response_data))
        self.assertEqual(docs, list(map(remove_system_fields, response_data)))

    def test_query_docs_by_fields(self):
        collection = self.try_create_collection('testdb', 'testcol')

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        docs = []
        with open(os.path.join(os.path.dirname(__file__), 'example.jl')) as f:
            for line in f.readlines():
                doc = json.loads(line)
                docs.append(doc)
                
        for doc in docs:
            client.post(self.build_api_collection_documents_url(collection), data=doc, format='json')

        response = client.get(self.build_api_collection_documents_url(collection) + '?fields=type,name')
        response_data = json.loads(response.content)['data']
        response_data_fields = set()
        for doc in response_data:
            for doc_field in doc.keys():
                response_data_fields.add(doc_field)

        self.assertEqual(3, len(response_data))
        self.assertEqual(set(['id', 'type', 'name']), response_data_fields)
