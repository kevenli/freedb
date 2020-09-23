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
        new_doc_id = res.json()[0]['id']
        self.assertIsNotNone(new_doc_id)

        res = self.client.get(f'/api/databases/{db_name}/collections/{col_name}/documents/{new_doc_id}')
        logger.debug(res.content)
        fetched_doc = res.json()
        self.assertIsNotNone(fetched_doc['_ts'])
