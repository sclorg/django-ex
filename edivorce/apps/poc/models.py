from django.db import models
from django.conf import settings

from edivorce.apps.core import redis


class Document(models.Model):
    """
    This is only a POC model and should not be loaded on a production system.
    """
    filename = models.CharField(max_length=128, null=True)  # saving the original filename separately
    file = models.FileField(upload_to=redis.generate_unique_filename, storage=redis.RedisStorage())

    def save(self, *args, **kwargs):
        self.filename = self.file.name

        super(Document, self).save(*args, **kwargs)
