import json

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
        self.another_user = BceidUser.objects.create(user_guid='5678')
        self.client = APIClient()
        self.default_doc_type = 'MC'
        self.default_party_code = 0

    def test_get_documents(self):
        url = reverse('documents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_documents(self):
        url = reverse('documents')
        self.assertEqual(Document.objects.count(), 0)

        file = self._create_file()
        data = {
            'file': file,
            'doc_type': 'AAI',
            'party_code': 1
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Document.objects.count(), 1)
        document = Document.objects.first()

        # Check document properties
        self.assertEqual(document.bceid_user, self.user)
        self.assertEqual(document.doc_type, 'AAI')
        self.assertEqual(document.party_code, 1)
        self.assertEqual(document.filename, file.name)
        self.assertEqual(document.size, file.size)

    def test_post_duplicate_files_not_allowed(self):
        url = reverse('documents')

        file = self._create_file()
        data = {
            'file': file,
            'doc_type': 'AAI',
            'party_code': 1
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)

        file.seek(0)  #
        response = self.client.post(url, data)
        self.assertContains(response,
                            'This file appears to have already been uploaded for this document.',
                            status_code=status.HTTP_400_BAD_REQUEST)

    def test_post_field_validation(self):
        url = reverse('documents')

        file = self._create_file(extension='HEIC')
        data = {
            'file': file,
            'doc_type': 'INVALID',
            'party_code': 3
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        self.assertEqual(Document.objects.count(), 0)

        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('File type not supported', json_response['file'][0])
        self.assertIn('Doc type not supported', json_response['doc_type'][0])
        self.assertIn('Ensure this value is less than or equal to 2', json_response['party_code'][0])

    def test_get_documents_meta_must_be_logged_in(self):
        url = reverse('documents-meta', kwargs={'doc_type': self.default_doc_type, 'party_code': self.default_party_code})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_documents_meta_no_documents(self):
        url = reverse('documents-meta', kwargs={'doc_type': self.default_doc_type, 'party_code': self.default_party_code})
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), 0)

    def test_get_documents_meta_some_documents(self):
        url = reverse('documents-meta', kwargs={'doc_type': self.default_doc_type, 'party_code': self.default_party_code})
        self.client.force_authenticate(self.user)
        doc_1 = self._create_document()
        doc_2 = self._create_document()
        self._create_document(party_code=1)
        self._create_document(doc_type='CSA')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), 2)
        self._response_data_equals_document(json_response[0], doc_1)
        self._response_data_equals_document(json_response[1], doc_2)

    def test_get_documents_meta_different_doc_type_party_code(self):
        url = reverse('documents-meta', kwargs={'doc_type': self.default_doc_type, 'party_code': self.default_party_code})
        self.client.force_authenticate(self.user)

        returned_doc = self._create_document()
        self._create_document(doc_type='CSA')
        self._create_document(party_code=1)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), 1)
        self._response_data_equals_document(json_response[0], returned_doc)

    def test_get_documents_meta_different_user(self):
        url = reverse('documents-meta', kwargs={'doc_type': self.default_doc_type, 'party_code': self.default_party_code})
        self.client.force_authenticate(self.user)

        self._create_document()
        self._create_document()

        self.client.force_authenticate(self.another_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), 0)

    def _create_document(self, doc_type=None, party_code=None):
        if not doc_type:
            doc_type = self.default_doc_type
        if not party_code:
            party_code = self.default_party_code
        new_file = self._create_file()
        document = Document(file=new_file, bceid_user=self.user, party_code=party_code, doc_type=doc_type)
        document.save()
        return document

    @staticmethod
    def _create_file(extension='jpg'):
        num_documents = Document.objects.count()
        new_file = SimpleUploadedFile(f'test_file_{num_documents + 1}.{extension}', b'test content')
        return new_file

    def _response_data_equals_document(self, response_doc, document_object):
        self.assertEqual(response_doc['doc_type'], document_object.doc_type)
        self.assertEqual(response_doc['party_code'], document_object.party_code)
        self.assertEqual(response_doc['filename'], document_object.filename)
        self.assertEqual(response_doc['size'], document_object.size)
        self.assertEqual(response_doc['rotation'], document_object.rotation)
        self.assertEqual(response_doc['sort_order'], document_object.sort_order)
        self.assertEqual(response_doc['file_url'], document_object.get_file_url())
