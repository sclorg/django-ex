from django.conf.urls import url

from edivorce.apps.poc import views
from ..core.decorators import bceid_required

urlpatterns = [
    url(r'scan', bceid_required(views.UploadScan.as_view()), name="poc-scan"),
    url(r'storage/doc/(?P<document_id>\d+)', views.view_document_file, name="poc-storage-download"),
    url(r'storage', bceid_required(views.UploadStorage.as_view()), name="poc-storage"),
]