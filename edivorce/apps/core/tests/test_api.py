from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import modify_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from edivorce.apps.core.models import BceidUser, Document


@modify_settings(MIDDLEWARE={'remove': 'edivorce.apps.core.middleware.bceid_middleware.BceidMiddleware',})
class APITest(APITestCase):
    def setUp(self):
        self.user = BceidUser.objects.create(user_guid='1234')
        self.client = APIClient()
        self.file = SimpleUploadedFile('test.pdf', b'test content')

    def test_get_unauthorized(self):
        url = reverse('documents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_unauthorized(self):
        data = {
            'file': self.file,
            'doc_type': 'AAI',
            'party_code': 1
        }
        url = reverse('documents')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post(self):
        self.assertEqual(Document.objects.count(), 0)

        self.client.login(username='lauren', password='secret')
        data = {
            'file': self.file,
            'doc_type': 'AAI',
            'party_code': 1
        }

        self.client.force_authenticate(self.user)
        url = reverse('documents')
        response = self.client.post(url, data, user=self.user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Document.objects.count(), 1)
        document = Document.objects.first()

        # Check document properties
        self.assertEqual(document.bceid_user, self.user)
        self.assertEqual(document.doc_type, 'AAI')
        self.assertEqual(document.party_code, 1)
        self.assertEqual(document.filename, self.file.name)
        self.assertEqual(document.size, self.file.size)
