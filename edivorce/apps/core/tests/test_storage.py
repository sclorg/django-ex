from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TransactionTestCase
from redis.exceptions import ConnectionError

from edivorce.apps.core.models import BceidUser, Document
from edivorce.apps.core.redis import generate_unique_filename


class UploadStorageTests(TransactionTestCase):
    def setUp(self):
        self.user = BceidUser.objects.create(user_guid='1234')

    @mock.patch('redis.connection.ConnectionPool.get_connection')
    def test_storage_connection_error(self, mock_redis):
        mock_redis.side_effect = ConnectionError()

        original_count = Document.objects.count()
        connection_error = False

        try:
            file = SimpleUploadedFile('file.txt', b'this is some content')
            test = Document()
            test.file = file
            test.doc_type = 'MC'
            test.bceid_user = self.user
            test.save()
        except ConnectionError:
            connection_error = True

        self.assertTrue(connection_error)
        self.assertEqual(Document.objects.count(), original_count)

    @mock.patch('edivorce.apps.core.redis.RedisStorage.get_available_name')
    @mock.patch('edivorce.apps.core.redis.RedisStorage._save')
    def test_storage_file_name_match(self, mock_redis_an, mock_redis_save):
        mock_redis_an.return_value = 'file.txt'
        mock_redis_save.return_value = 'file.txt'

        file = SimpleUploadedFile('file.txt', b'this is some content')
        test = Document()
        test.file = file
        test.doc_type = 'MC'
        test.bceid_user = self.user
        test.save()

        self.assertTrue(mock_redis_save.called)
        self.assertEqual(test.filename, test.file.name)

    @mock.patch('edivorce.apps.core.redis.RedisStorage.get_available_name')
    @mock.patch('edivorce.apps.core.redis.RedisStorage._save')
    def test_storage_redis_storage(self, mock_redis_an, mock_redis_save):
        mock_redis_an.return_value = '6061bebb-f2be-4a74-8757-c4063f6f6993_file_txt'
        mock_redis_save.return_value = 'file.txt'

        file = SimpleUploadedFile('file.txt', b'this is some content')
        test = Document()
        test.file = file
        test.doc_type = 'MC'
        test.bceid_user = self.user
        test.save()

        self.assertTrue(mock_redis_save.called)
        self.assertEqual(Document.objects.count(), 1)
        test = Document.objects.get(id=test.id)
        self.assertEqual(test.filename, 'file.txt')
        self.assertNotEqual(test.file.name, 'file.txt')

    def test_storage_redis_key(self):
        name = 'file.txt'
        self.assertNotEqual(generate_unique_filename(None, name), name)

        name = '../../../etc/passwd'
        self.assertNotEqual(generate_unique_filename(None, name), name)
        self.assertFalse('../../' in generate_unique_filename(None, name))

        name = '../../../etc/passwd%00.png'
        self.assertNotEqual(generate_unique_filename(None, name), name)
        self.assertFalse('../../' in generate_unique_filename(None, name))

        name = '..%2F..%2F..%2Fetc%2F'
        self.assertNotEqual(generate_unique_filename(None, name), name)
        self.assertFalse('../../' in generate_unique_filename(None, name))

    @mock.patch('edivorce.apps.core.redis.RedisStorage.get_available_name')
    @mock.patch('edivorce.apps.core.redis.RedisStorage._save')
    @mock.patch('edivorce.apps.core.redis.RedisStorage.delete')
    def test_storage_redis_delete(self, mock_redis_an, mock_redis_save, mock_redis_delete):
        mock_redis_an.return_value = '6061bebb-f2be-4a74-8757-c4063f6f6993_file_txt'
        mock_redis_save.return_value = 'file.txt'
        mock_redis_delete.return_value = True

        file = SimpleUploadedFile('file.txt', b'this is some content')
        test = Document()
        test.file = file
        test.doc_type = 'MC'        
        test.bceid_user = self.user
        test.save()

        test.delete()

        self.assertTrue(mock_redis_delete.called)
