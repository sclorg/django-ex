from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from edivorce.apps.poc import views

urlpatterns = [
    url(r'scan', login_required(views.UploadScan.as_view()), name="poc-scan"),
    url(r'hub', login_required(views.EFilingSubmissionUpload.as_view()), name="poc-hub"),
    url(r'storage/doc/(?P<document_id>\d+)', login_required(views.view_document_file), name="poc-storage-download"),
    url(r'storage/delete/(?P<pk>\d+)', login_required(views.UploadStorageDelete.as_view()), name="poc-storage-delete"),
    url(r'storage', login_required(views.UploadStorage.as_view()), name="poc-storage"),
]