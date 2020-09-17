from django.db import models
from django.conf import settings

from edivorce.apps.core import redis


class Document(models.Model):
    """
    This is only a POC model and should not be loaded on a production system.
    """
    filename = models.CharField(max_length=128, null=True)  # saving the original filename separately
    file = models.FileField(upload_to=redis.generate_unique_filename, storage=redis.RedisStorage())
    docType = models.CharField(max_length=4, null=True, blank=True)
    partyId = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.filename = self.file.name

        super(Document, self).save(*args, **kwargs)

    def delete(self, **kwargs):
        """
        Override delete so we can delete the Redis object when this instance is deleted.
        :param kwargs:
        :return:
        """
        self.file.delete(save=False)

        super(Document, self).delete(**kwargs)
