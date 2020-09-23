from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from freedb import views

factory = APIRequestFactory()
user, _= User.objects.get_or_create(username='test')
user.save()
user.refresh_from_db()


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