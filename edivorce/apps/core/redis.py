"""
Redis storages backend to help store binary data.
"""
import base64
import io
import redis
import uuid
import re

from shutil import copyfileobj
from tempfile import SpooledTemporaryFile

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

EX_EXPIRY = 60*60*24*30  # 1 month expiry in seconds


def generate_unique_filename(instance, filename):
    return '{}_{}'.format(uuid.uuid4(), re.sub('[^0-9a-zA-Z]+', '_', filename))


class RedisFile(File):

    def __init__(self, name, storage):
        self.name = name
        self._storage = storage
        self._file = None

    def _get_file(self):
        if self._file is None:
            self._file = SpooledTemporaryFile()

            # get from redis
            content = self._storage.client.get(self.name)

            # stored as base64 .. decode
            content = base64.b64decode(content)

            with io.BytesIO(content) as file_content:
                copyfileobj(file_content, self._file)

            self._file.seek(0)
        return self._file

    def _set_file(self, value):
        self._file = value

    file = property(_get_file, _set_file)


@deconstructible
class RedisStorage(Storage):
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD
        )

    def _full_key_name(self, name):
        return name

    def delete(self, name):
        self.client.delete(self._full_key_name(name))

    def exists(self, name):
        return self.client.exists(self._full_key_name(name))

    def listdir(self, path):
        return '', ''

    def size(self, name):
        return ''

    def url(self, name):
        return ''

    def _open(self, name, mode='rb'):
        remote_file = RedisFile(self._full_key_name(name), self)
        return remote_file

    def _save(self, name, content):
        content.open()

        data = base64.b64encode(content.read())
        self.client.set(self._full_key_name(name), data, ex=EX_EXPIRY)

        content.close()
        return name

    def get_available_name(self, name, max_length=None):
        """
        Allow storage backend to generate a new name if there is already an existing file. Not used for this Redis
        implementation.
        """
        name = self._full_key_name(name)
        return super().get_available_name(name, max_length)


