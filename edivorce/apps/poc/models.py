from django.db import models
from django.conf import settings
from edivorce.apps.core.models import BceidUser

from edivorce.apps.core import redis


class Document(models.Model):
    """
    This is only a POC model and should not be loaded on a production system.
    """
    filename = models.CharField(max_length=128, null=True)  # saving the original filename separately
    """ File name and extension """

    size = models.IntegerField(default=0)
    """ Size of the file (size and name uniquely identify each file on the input) """

    file = models.FileField(upload_to=redis.generate_unique_filename, storage=redis.RedisStorage())
    """ File temporarily stored in Redis """    
    
    doc_type = models.CharField(max_length=4, null=True, blank=True)
    """ CEIS Document Type Code (2-4 letters) """

    party_code = models.IntegerField(default=0)
    """ 1 = You, 2 = Your Spouse, 0 = Shared """

    sort_order = models.IntegerField(default=1)
    """ file order (page number in the PDF) """

    rotation = models.IntegerField(default=0)
    """ 0, 90, 180 or 270 """
    
    bceid_user = models.ForeignKey(BceidUser, related_name='uploads', on_delete=models.CASCADE)
    """ User who uploaded the attachment """

    date_uploaded = models.DateTimeField(auto_now_add=True)
    """ Date the record was last updated """

    class Meta:
        unique_together = ("bceid_user", "doc_type", "party_code", "filename", "size")

    def save(self, *args, **kwargs):
        self.filename = self.file.name
        self.size = self.file.size

        super(Document, self).save(*args, **kwargs)

    def delete(self, **kwargs):
        """
        Override delete so we can delete the Redis object when this instance is deleted.
        :param kwargs:
        :return:
        """
        self.file.delete(save=False)

        super(Document, self).delete(**kwargs)
