import json
from unittest import mock
from unittest.util import safe_repr

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import modify_settings, override_settings
from django.urls import reverse
from graphene_django.utils import GraphQLTestCase
from redis import Redis
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from edivorce.apps.core.models import BceidUser, Document


class MockRedis:
    """Imitate a Redis object so unit tests can run on our GitHub test server without needing a real
        Redis server."""

    # The 'Redis' store
    fake_redis = {}

    def delete(self, key):
        if key in MockRedis.fake_redis:
            del MockRedis.fake_redis[key]

    def exists(self, key):
        return key in MockRedis.fake_redis

    def get(self, key):
        result = '' if key not in MockRedis.fake_redis else MockRedis.fake_redis[key]
        return result

    def set(self, name, value, *args, **kwargs):
        MockRedis.fake_redis[name] = value
        return name


@mock.patch.object(Redis, 'set', MockRedis.set)
@mock.patch.object(Redis, 'get', MockRedis.get)
@mock.patch.object(Redis, 'delete', MockRedis.delete)
@mock.patch.object(Redis, 'exists', MockRedis.exists)
@modify_settings(MIDDLEWARE={'remove': 'edivorce.apps.core.middleware.bceid_middleware.BceidMiddleware'})
@override_settings(CLAMAV_ENABLED=False)
class APITest(APITestCase):
    def setUp(self):
        self.user = _get_or_create_user(user_guid='1234')
        self.another_user = _get_or_create_user(user_guid='5678')
        self.client = APIClient()
        self.default_doc_type = 'MC'
        self.default_party_code = 0

    def test_get_documents(self):
        url = reverse('documents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_documents(self):
        url = reverse('documents')
        self.assertEqual(Document.objects.count(), 0)

        file = _create_file()
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
        self.assertEqual(document.rotation, 0)
        self.assertEqual(document.sort_order, 1)

    def test_post_duplicate_files_not_allowed(self):
        url = reverse('documents')

        file = _create_file()
        data = {
            'file': file,
            'doc_type': 'AAI',
            'party_code': 1
        }
        self.client.force_authenticate(self.user)

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)

        file.seek(0)

        response = self.client.post(url, data)

        self.assertContains(response,
                            'This file appears to have already been uploaded for this document.',
                            status_code=status.HTTP_400_BAD_REQUEST)

    def test_post_only_one_pdf(self):
        url = reverse('documents')

        file = _create_file()
        data = {
            'file': file,
            'doc_type': 'AAI',
            'party_code': 1
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)

        file = _create_file(extension='pdf')
        data = {
            'file': file,
            'doc_type': 'AAI',
            'party_code': 1
        }

        response = self.client.post(url, data)

        self.assertContains(response,
                            "Only one PDF is allowed per form, and PDF documents cannot be combined with images.",
                            status_code=status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Document.objects.count(), 1)

    def test_post_no_existing_pdfs(self):
        url = reverse('documents')

        file = _create_file(extension='pdf')
        data = {
            'file': file,
            'doc_type': 'AAI',
            'party_code': 1
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)

        file = _create_file()
        data = {
            'file': file,
            'doc_type': 'AAI',
            'party_code': 1
        }

        response = self.client.post(url, data)

        self.assertContains(response,
                            "PDF documents cannot be combined with images. Only a single PDF or multiple images can be uploaded into one form.",
                            status_code=status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Document.objects.count(), 1)

    def test_post_field_validation(self):
        url = reverse('documents')

        file = _create_file(extension='HEIC')
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

    def test_get_file(self):
        document = self._create_document()
        self.assertEqual(Document.objects.count(), 1)
        url = document.get_file_url()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.another_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, document.file.read())

    def test_get_file_missing_from_redis(self):
        document = self._create_document()
        self._create_document()
        another_document = self._create_document(party_code=2)

        self.assertEqual(Document.objects.count(), 3)
        url = document.get_file_url()

        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, document.file.read())

        # Delete file from redis
        document.file.delete()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Document.objects.first(), another_document)

    def test_get_file_by_key(self):
        document = self._create_document()
        url = reverse('file_by_key', kwargs={'file_key': document.file.name, 'rotation': 0})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, document.file.read())

        # Delete file from redis
        document.file.delete()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_document(self):
        document = self._create_document()
        self.assertEqual(Document.objects.count(), 1)
        url = document.get_file_url()

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Document.objects.count(), 1)

        self.client.force_authenticate(self.another_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Document.objects.count(), 1)

        self.client.force_authenticate(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Document.objects.count(), 0)

    def test_update_document(self):
        document = self._create_document()
        url = document.get_file_url()

        data = {
            'rotation': 90
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.another_user)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data['rotation'] = 45
        response = self.client.put(url, data)
        self.assertContains(response,
                            'Rotation must be 0, 90, 180, or 270',
                            status_code=status.HTTP_400_BAD_REQUEST)

    def _create_document(self, doc_type=None, party_code=None):
        if not doc_type:
            doc_type = self.default_doc_type
        if not party_code:
            party_code = self.default_party_code
        new_file = _create_file()
        document = Document(file=new_file, bceid_user=self.user, party_code=party_code, doc_type=doc_type)
        document.save()
        return document

    def _response_data_equals_document(self, response_doc, document_object):
        self.assertEqual(response_doc['doc_type'], document_object.doc_type)
        self.assertEqual(response_doc['party_code'], document_object.party_code)
        self.assertEqual(response_doc['filename'], document_object.filename)
        self.assertEqual(response_doc['size'], document_object.size)
        self.assertEqual(response_doc['rotation'], document_object.rotation)
        self.assertEqual(response_doc['sort_order'], document_object.sort_order)
        self.assertEqual(response_doc['file_url'], document_object.get_file_url())


@mock.patch.object(Redis, 'set', MockRedis.set)
@mock.patch.object(Redis, 'get', MockRedis.get)
@mock.patch.object(Redis, 'delete', MockRedis.delete)
@mock.patch.object(Redis, 'exists', MockRedis.exists)
class GraphQLAPITest(GraphQLTestCase):
    GRAPHQL_URL = reverse('graphql')

    def setUp(self):
        self.user = _get_or_create_user(user_guid='1234')
        self.another_user = _get_or_create_user(user_guid='5678')
        self.default_doc_type = 'MC'
        self.default_party_code = 0

    def _login(self):
        self._client.force_login(self.user)

    def test_not_logged_in(self):
        response = self.query('{documents{filename}}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.query('''
                mutation ($input: DocumentMetaDataInput!) {
                  updateMetadata(input: $input) {
                    documents {
                      filename
                    }
                  }
                }''', input_data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_get_excluded_fields(self):
        self._login()
        response = self.query('{documents{id file}}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContainsError('Cannot query field "id"', response)
        self.assertContainsError('Cannot query field "file"', response)

    def test_must_specify_doctype_partycode(self):
        self._login()
        response = self.query('{documents{filename}}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContainsError('argument "docType" of type "String!" is required but not provided', response)
        self.assertContainsError('argument "partyCode" of type "Int!" is required but not provided', response)

    def test_get_only_returns_user_form_docs(self):
        self._login()
        doc = self._create_document()
        self._create_document(user=self.another_user)
        self._create_document(doc_type='AAI')
        self._create_document(party_code=2)

        response = self.query('''
        {
            documents (docType: "MC", partyCode: 0) {
                filename
            }
        }''')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseNoErrors(response)

        content = json.loads(response.content)['data']
        self.assertEqual(len(content['documents']), 1)
        self.assertEqual(content['documents'][0]['filename'], doc.filename)

    def test_missing_redis_document_deletes_all_documents(self):
        self._login()

        doc_1 = self._create_document()
        doc_2 = self._create_document()
        doc_3 = self._create_document()
        another_doc = self._create_document(party_code=2)

        self.assertEqual(Document.objects.count(), 4)

        query = '''
         {
             documents (docType: "MC", partyCode: 0) {
                 filename
             }
         }'''
        response = self.query(query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseNoErrors(response)

        content = json.loads(response.content)['data']
        self.assertEqual(len(content['documents']), 3)
        self.assertEqual(content['documents'][0]['filename'], doc_1.filename)
        self.assertEqual(content['documents'][1]['filename'], doc_2.filename)
        self.assertEqual(content['documents'][2]['filename'], doc_3.filename)

        # Delete file from Redis
        doc_1.file.delete()
        response = self.query(query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)['data']
        self.assertEqual(len(content['documents']), 0)

        # All files in for that doc_type/party_code/user were deleted
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Document.objects.first(), another_doc)

    def test_update_metadata(self):
        doc_1 = self._create_document()
        doc_2 = self._create_document()

        input_data = {
            "docType": doc_1.doc_type,
            "partyCode": doc_1.party_code,
            "files": [
                {
                    'filename': doc_2.filename,
                    'size': doc_2.size,
                    'width': 600,
                    'height': 800
                },
                {
                    'filename': doc_1.filename,
                    'size': doc_1.size,
                    'rotation': 270
                },
            ]
        }
        query = '''
                mutation ($input: DocumentMetaDataInput!) {
                  updateMetadata(input: $input) {
                    documents {
                      filename
                    }
                  }
                }
            '''
        self._login()
        response = self.query(query, input_data=input_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseNoErrors(response)

        doc_1.refresh_from_db()
        doc_2.refresh_from_db()
        self.assertEqual(doc_1.sort_order, 2)
        self.assertEqual(doc_1.rotation, 270)
        self.assertEqual(doc_2.sort_order, 1)
        self.assertEqual(doc_2.width, 600)
        self.assertEqual(doc_2.height, 800)

    def test_update_metadata_too_few_files(self):
        doc_1 = self._create_document()
        doc_2 = self._create_document()

        input_data = {
            "docType": doc_1.doc_type,
            "partyCode": doc_1.party_code,
            "files": [
                {
                    'filename': doc_2.filename,
                    'size': doc_2.size,
                    'rotation': 180,
                    'width': 600,
                    'height': 800
                }
            ]
        }
        query = '''
                mutation ($input: DocumentMetaDataInput!) {
                  updateMetadata(input: $input) {
                    documents {
                      filename
                    }
                  }
                }
            '''
        self._login()
        response = self.query(query, input_data=input_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseHasErrors(response)
        self.assertContainsError('there must be the same number of files', response)

    def assertContainsError(self, msg, response):
        content = json.loads(response.content)
        errors = [error['message'] for error in content['errors']]
        for error in errors:
            if msg in error:
                break
        else:
            error_msgs = "\n".join([safe_repr(error) for error in errors])
            fail_message = f'Message: {safe_repr(msg)}\nNot found in errors:\n{error_msgs}'
            self.fail(fail_message)

    def _create_document(self, user=None, doc_type=None, party_code=None):
        if not doc_type:
            doc_type = self.default_doc_type
        if not party_code:
            party_code = self.default_party_code
        if not user:
            user = self.user
        new_file = _create_file()
        document = Document(file=new_file, bceid_user=user, party_code=party_code, doc_type=doc_type)
        document.save()
        return document


def _create_file(extension='jpg'):
    num_documents = Document.objects.count()
    new_file = SimpleUploadedFile(f'test_file_{num_documents + 1}.{extension}', b'test content')
    return new_file


def _get_or_create_user(user_guid):
    try:
        return BceidUser.objects.get(user_guid=user_guid)
    except BceidUser.DoesNotExist:
        return BceidUser.objects.create(user_guid=user_guid, username=user_guid)
