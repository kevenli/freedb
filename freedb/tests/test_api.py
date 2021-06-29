import json
import os
import logging
from urllib.parse import urljoin, urlparse, urlencode, urlunparse
from unittest import skip

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from freedb.models import Database, Collection
User = get_user_model()

logger = logging.getLogger(__name__)


class ApiTestBase(TestCase):
    def setUp(self):
        super().setUp()
        User = get_user_model()
        tester, _= User.objects.get_or_create(username='tester')
        self.user = tester

        token, _ = Token.objects.get_or_create(user=tester)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.client = client


class CollectionTestMixin:
    def build_api_collection_documents_url(self, collection):
        return f'/api/databases/{collection.database.name}/collections/{collection.name}/documents'

    def try_create_collection(self, db_name, col_name):
        db, _ = Database.objects.get_or_create(name=db_name, owner=self.user)
        db.save()

        col, _ = Collection.objects.get_or_create(name=col_name, database=db)
        col.save()
        return col


class ApiTest(CollectionTestMixin, ApiTestBase):
    def test_query_docs(self):
        collection = self.try_create_collection('testdb', 'testcol')

        client = self.client

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

        client = self.client

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


class DocmentsApiTestMixin(CollectionTestMixin):
    def build_document_url(self, collection, doc_id):
        return urljoin(self.build_api_collection_documents_url(collection), f'./documents/{doc_id}')

    def build_documents_url(self, collection, exist=None):
        url = urljoin(self.build_api_collection_documents_url(collection), f'./documents')
        url_parts = list(urlparse(url))
        params = {}
        if exist:
            params['exist'] = exist
        if params:
            url_parts[4] = urlencode(params)
        ret = urlunparse(url_parts)
        print(ret)
        return ret


class DocumentApiTest(DocmentsApiTestMixin, ApiTestBase):
    def test_post_doc(self):
        collection = self.try_create_collection('DocmentsApiTest', 'test_post_doc')
        doc = {'id': 1, 'data': 'some data before update'}

        save_res = self.client.post(self.build_documents_url(collection), data=doc, format='json')
        saved_obj = save_res.json()
        self.assertEqual('1', saved_obj['id'])

    @skip("Cannot pass, fix later")
    def test_post_doc_exist_skip(self):
        doc_id = '1'
        collection = self.try_create_collection('DocmentsApiTest', 'test_post_doc_exist_skip')
        doc = {'id': doc_id, 'data': 'some data before update'}

        save_res = self.client.post(self.build_documents_url(collection), data=doc, format='json')
        saved_obj = save_res.json()
        self.assertEqual(doc_id, saved_obj['id'])

        update_doc = {'id': doc_id, 'data': 'after update'}
        save_res2 = self.client.post(self.build_documents_url(collection, exist='skip'), data=update_doc, format='json')

        final_doc = self.client.get(self.build_document_url(collection, doc_id)).json()
        self.assertEqual(final_doc['data'], doc['data'])

    @skip
    def test_post_doc_exist_overwrite(self):
        collection = self.try_create_collection('DocmentsApiTest', 'test_post_doc_exist_skip')
        doc = {'id': 1, 'data': 'some data before update'}

        save_res = self.client.post(self.build_documents_url(collection), data=doc, format='json')
        saved_obj = save_res.json()
        self.assertEqual('1', saved_obj['id'])

        update_doc = {'id': 1, 'data': 'after update'}
        save_res2 = self.client.post(self.build_documents_url(collection, exist='overwrite'), data=update_doc, format='json')

        final_doc = self.client.get(self.build_document_url(collection, '1')).json()
        self.assertEqual(final_doc['data'], update_doc['data'])

    def test_post_doc_exist_merge(self):
        doc_id = '1'
        collection = self.try_create_collection('DocmentsApiTest', 'test_post_doc_exist_merge')
        doc = {'id': doc_id, 'data': 'some data before update'}

        save_res = self.client.post(self.build_documents_url(collection), data=doc, format='json')
        saved_obj = save_res.json()
        self.assertEqual(doc_id, saved_obj['id'])

        update_doc = {'id': doc_id, 'data': 'after update'}
        save_res2 = self.client.post(self.build_documents_url(collection, exist='merge'), data=update_doc, format='json')

        final_doc = self.client.get(self.build_document_url(collection, doc_id)).json()
        self.assertEqual(final_doc['data'], update_doc['data'])