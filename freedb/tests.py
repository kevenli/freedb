import json
import logging
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from freedb import views

factory = APIRequestFactory()
user, _= User.objects.get_or_create(username='test')
user.save()
user.refresh_from_db()


logger = logging.getLogger(__name__)


class ApiDatabasesTest(TestCase):
    def test_post_databases(self):
        user, _= User.objects.get_or_create(username='test')

        request = factory.post('/api/databases', data={'name': 'ApiDatabasesTest'})
        force_authenticate(request, user=user)
        view = views.DatabaseList.as_view()
        #self.client
        #self.assertEqual(200, res.status_code)
        res = view(request)
        self.assertEqual(200, res.status_code)


class DatabaseCollectionDocumentInstanceTest(TestCase):
    def test_delete(self):
        user, _= User.objects.get_or_create(username='test')
        db_name = 'DatabaseCollectionDocumentInstanceTest'
        col_name = 'test_delete'

        self.client.force_login(user)
        res = self.client.post('/api/databases', data={'name': db_name})
        self.assertEqual(200, res.status_code)

        res = self.client.post(f'/api/databases/{db_name}/collections', data={'name': col_name})
        self.assertEqual(200, res.status_code)

        res = self.client.delete(f'/api/databases/{db_name}/collections/{col_name}/documents')
        self.assertEqual(200, res.status_code)

        res = self.client.delete(f'/api/databases/{db_name}/collections/{col_name}/documents/1')
        self.assertEqual(404, res.status_code)

        post_doc = {'a':1}
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents', 
                               data=post_doc, 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)
        new_doc_id = res.json()['id']

        res = self.client.delete(f'/api/databases/{db_name}/collections/{col_name}/documents/{new_doc_id}')
        self.assertEqual(200, res.status_code)






class DatabaseCollectionDocumentsTest(TestCase):
    def test_post(self):
        user, _= User.objects.get_or_create(username='test')
        db_name = 'DatabaseCollectionDocumentsTest'
        col_name = 'test'

        self.client.force_login(user)
        res = self.client.post('/api/databases', data={'name': 'DatabaseCollectionDocumentsTest'})
        self.assertEqual(200, res.status_code)

        res = self.client.post(f'/api/databases/{db_name}/collections', data={'name': col_name})
        self.assertEqual(200, res.status_code)

        doc = {'a': 1}
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents', data=doc)
        self.assertEqual(200, res.status_code)
        new_doc_id = res.json()['id']
        self.assertIsNotNone(new_doc_id)

        res = self.client.get(f'/api/databases/{db_name}/collections/{col_name}/documents/{new_doc_id}')
        logger.debug(res.content)
        fetched_doc = res.json()
        self.assertIsNotNone(fetched_doc['_ts'])

    def test_post_merge(self):
        user, _= User.objects.get_or_create(username='test')
        db_name = 'DatabaseCollectionDocumentsTest'
        col_name = 'test_post_merge'

        self.client.force_login(user)
        res = self.client.post('/api/databases', data={'name': 'DatabaseCollectionDocumentsTest'})
        self.assertEqual(200, res.status_code)

        res = self.client.post(f'/api/databases/{db_name}/collections', data={'name': col_name})
        self.assertEqual(200, res.status_code)

        doc = {'id': 'x', 'a': 1}
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents', 
                               data=doc, 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)
        saved_doc = res.json()
        new_doc_id = saved_doc['id']
        self.assertIsNotNone(new_doc_id)
        self.assertEqual(1, saved_doc['a'])

        doc = {'id': 'x', 'b': 2}
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents?exist=merge', 
                               data=doc, 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)
        saved_doc = res.json()
        self.assertEqual(1, saved_doc['a'])
        self.assertEqual(2, saved_doc['b'])

        res = self.client.get(f'/api/databases/{db_name}/collections/{col_name}/documents/{new_doc_id}')
        logger.debug(res.content)
        fetched_doc = res.json()
        self.assertIsNotNone(fetched_doc['_ts'])

    def test_post_merge_none_exist(self):
        user, _= User.objects.get_or_create(username='test')
        db_name = 'DatabaseCollectionDocumentsTest'
        col_name = 'test_post_merge_none_exist'

        self.client.force_login(user)
        res = self.client.post('/api/databases', data={'name': db_name})
        self.assertEqual(200, res.status_code)

        res = self.client.post(f'/api/databases/{db_name}/collections', data={'name': col_name})
        self.assertEqual(200, res.status_code)

        doc = {'id': 'x', 'a': 1}
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents?exist=merge', 
                               data=doc, 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)
        saved_doc = res.json()
        new_doc_id = saved_doc['id']
        self.assertIsNotNone(new_doc_id)
        self.assertEqual(1, saved_doc['a'])
        self.assertIsNotNone(saved_doc['_ts'])

        res = self.client.get(f'/api/databases/{db_name}/collections/{col_name}/documents/{new_doc_id}')
        logger.debug(res.content)
        fetched_doc = res.json()
        self.assertIsNotNone(fetched_doc['_ts'])

    def test_post_overwrite(self):
        user, _= User.objects.get_or_create(username='test')
        db_name = 'DatabaseCollectionDocumentsTest'
        col_name = 'test_post_overwrite'

        self.client.force_login(user)
        res = self.client.post('/api/databases', data={'name': 'DatabaseCollectionDocumentsTest'})
        self.assertEqual(200, res.status_code)

        res = self.client.post(f'/api/databases/{db_name}/collections', data={'name': col_name})
        self.assertEqual(200, res.status_code)

        res = self.client.delete(f'/api/databases/{db_name}/collections/{col_name}/documents')
        self.assertEqual(200, res.status_code)

        doc = {'id': 'x', 'a': 1}
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents', 
                               data=doc, 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)
        saved_doc = res.json()
        new_doc_id = saved_doc['id']
        self.assertIsNotNone(new_doc_id)
        self.assertEqual(1, saved_doc['a'])

        doc = {'id': 'x', 'b': 2}
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents?exist=overwrite', 
                               data=doc, 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)
        saved_doc = res.json()
        self.assertTrue('a' not in saved_doc)
        self.assertEqual(2, saved_doc['b'])
        self.assertIsNotNone(saved_doc['_ts'])

        res = self.client.get(f'/api/databases/{db_name}/collections/{col_name}/documents/{new_doc_id}')
        logger.debug(res.content)
        fetched_doc = res.json()
        self.assertIsNotNone(fetched_doc['_ts'])

    def test_delete(self):
        user, _= User.objects.get_or_create(username='test')
        db_name = 'DatabaseCollectionDocumentsTest'
        col_name = 'test_delete'
        self.client.force_login(user)
        res = self.client.post('/api/databases', data={'name': 'DatabaseCollectionDocumentsTest'})
        self.assertEqual(200, res.status_code)

        res = self.client.post(f'/api/databases/{db_name}/collections', data={'name': col_name})
        self.assertEqual(200, res.status_code)

        doc = {'id': 1, 'value': 2}
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents',
                               data=json.dumps(doc), 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)

        res = self.client.get(f'/api/databases/{db_name}/collections/{col_name}/documents')
        self.assertEqual(200, res.status_code)
        self.assertEqual(1, len(res.json()['data']))

        res = self.client.delete(f'/api/databases/{db_name}/collections/{col_name}/documents')
        self.assertEqual(200, res.status_code)

        res = self.client.get(f'/api/databases/{db_name}/collections/{col_name}/documents')
        self.assertEqual(200, res.status_code)
        self.assertEqual(0, len(res.json()['data']))

    def test_get_paging(self):
        user, _= User.objects.get_or_create(username='test')
        db_name = 'DatabaseCollectionDocumentsTest'
        col_name = 'test_get_paging'
        self.client.force_login(user)
        res = self.client.post('/api/databases', data={'name': db_name})
        self.assertEqual(200, res.status_code)

        res = self.client.post(f'/api/databases/{db_name}/collections', data={'name': col_name})
        self.assertEqual(200, res.status_code)

        doc = {'id': 1, 'value': 2}
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents',
                               data=json.dumps(doc), 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)

        res = self.client.delete(f'/api/databases/{db_name}/collections/{col_name}/documents')
        self.assertEqual(200, res.status_code)

        docs = [{
            'id': i
        } for i in range(500)]
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents:batchsave', 
                               data=json.dumps(docs), 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)

        page_size = 20
        last_ts = 0
        res = self.client.get(f'/api/databases/{db_name}/collections/{col_name}/documents')
        self.assertEqual(200, res.status_code)
        res_data = res.json()
        self.assertEqual(20, len(res_data['data']))
            
            
class DatabaseCollectionDocumentsSyncTest(TestCase):
    def test_get(self):
        user, _= User.objects.get_or_create(username='test')
        db_name = 'DatabaseCollectionDocumentsTest'
        col_name = 'test_get_paging'
        self.client.force_login(user)
        res = self.client.post('/api/databases', data={'name': db_name})
        self.assertEqual(200, res.status_code)

        res = self.client.post(f'/api/databases/{db_name}/collections', data={'name': col_name})
        self.assertEqual(200, res.status_code)

        doc = {'id': 1, 'value': 2}
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents',
                               data=json.dumps(doc), 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)

        res = self.client.delete(f'/api/databases/{db_name}/collections/{col_name}/documents')
        self.assertEqual(200, res.status_code)

        docs = [{
            'id': i
        } for i in range(500)]
        res = self.client.post(f'/api/databases/{db_name}/collections/{col_name}/documents:batchsave', 
                               data=json.dumps(docs), 
                               content_type='application/json')
        self.assertEqual(200, res.status_code)

        def sync_fetch(client, db_name, col_name, page_token=None):
            url = f'/api/databases/{db_name}/collections/{col_name}/documents:sync'
            if page_token:
                url += '?page_token=' + page_token
            res = client.get(url)
            return res

        res = sync_fetch(self.client, db_name, col_name)
        res_data = res.json()
        page_token = res_data['next_page_token']
        logger.debug(page_token)
        seen_ids = set()
        while len(res_data['docs']) > 0:
            for doc in res_data['docs']:
                logger.debug(doc)
                logger.debug(seen_ids)
                self.assertTrue(doc['id'] not in seen_ids)
                seen_ids.add(doc['id'])

            res = sync_fetch(self.client, db_name, col_name, page_token)
            res_data = res.json()
            page_token = res_data['next_page_token']

        self.assertEqual(500, len(seen_ids))

    def init_collection(self, col_name):
        user, _= User.objects.get_or_create(username='test')
        db_name = 'DatabaseCollectionDocumentsTest'
        self.client.force_login(user)
        res = self.client.post('/api/databases', data={'name': db_name})
        self.assertIn(res.status_code, [200, 409])

        res = self.client.post(f'/api/databases/{db_name}/collections', data={'name': col_name})
        self.assertIn(res.status_code, [200, 409])

        res = self.client.delete(f'/api/databases/{db_name}/collections/{col_name}/documents')
        self.assertEqual(200, res.status_code)

    def test_post_no_doc(self):
        db_name = 'DatabaseCollectionDocumentsTest'
        col_name = 'test_post_no_doc'

        self.init_collection(col_name)

        res = self.client.get(f'/api/databases/{db_name}/collections/{col_name}/documents:sync')
        self.assertEqual(200, res.status_code)
        self.assertEqual(None, res.json()['next_page_token'])


class CollectionFieldsTest(TestCase):
    def test_post(self):
        user, _= User.objects.get_or_create(username='test')
        db_name = 'DatabaseCollectionDocumentsTest'
        col_name = 'CollectionFieldsTest'

        self.client.force_login(user)
        res = self.client.post('/api/databases', data={'name': 'DatabaseCollectionDocumentsTest'})
        self.assertIn(res.status_code, [200, 409])

        res = self.client.post(f'/api/databases/{db_name}/collections', data={'name': col_name})
        self.assertIn(res.status_code, [200, 409])

        fields = [{
            'name': 'url',
            'type': 'string',
        }]
        res = self.client.put(f'/api/databases/{db_name}/collections/{col_name}/fields', 
                              data=json.dumps(fields), content_type='application/json')
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res['Content-Type'])
        fetch_fields = res.json()
        self.assertEqual(len(fields), len(fetch_fields))
        self.assertEqual(fields[0]['name'], fetch_fields[0]['name'])
        self.assertEqual(fields[0]['type'], fetch_fields[0]['type'])

        res = self.client.get(f'/api/databases/{db_name}/collections/{col_name}/fields')
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res['Content-Type'])
        fetch_fields = res.json()
        self.assertEqual(len(fields), len(fetch_fields))
        self.assertEqual(fields[0]['name'], fetch_fields[0]['name'])
        self.assertEqual(fields[0]['type'], fetch_fields[0]['type'])
