from django.conf.urls import url

from edivorce.apps.poc import views
from ..core.decorators import bceid_required

urlpatterns = [
    url(r'scan', bceid_required(views.UploadScan.as_view()), name="poc-scan"),
    url(r'hub', bceid_required(views.EfilingHubUpload.as_view()), name="poc-hub"),
    url(r'storage/doc/(?P<document_id>\d+)', bceid_required(views.view_document_file), name="poc-storage-download"),
    url(r'storage/delete/(?P<pk>\d+)', bceid_required(views.UploadStorageDelete.as_view()), name="poc-storage-delete"),
    url(r'storage', bceid_required(views.UploadStorage.as_view()), name="poc-storage"),
]