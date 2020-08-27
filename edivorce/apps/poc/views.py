from django.shortcuts import render
from django.views.generic.edit import FormView, CreateView, DeleteView
from django import forms
from django.http import HttpResponse

from edivorce.apps.core.validators import file_scan_validation
from edivorce.apps.poc.models import Document

"""
Everything in this file is considered as proof of concept work and should not be used for production code.
"""


class UploadScanForm(forms.Form):
    upload_file = forms.FileField(validators=[file_scan_validation])


class UploadScan(FormView):
    form_class = UploadScanForm
    template_name = "scan.html"

    def form_valid(self, form):
        context = self.get_context_data()
        context['validation_success'] = True
        return render(self.request, self.template_name, context)


class UploadStorage(CreateView):
    model = Document
    fields = ['file']
    template_name = "storage.html"
    success_url = '/poc/storage'

    def get_context_data(self, **kwargs):
        kwargs['documents'] = Document.objects.all()
        return super(UploadStorage, self).get_context_data(**kwargs)


class UploadStorageDelete(DeleteView):
    model = Document
    success_url = '/poc/storage'


def view_document_file(request, document_id):
    doc = Document.objects.get(id=document_id)

    content_type = 'application/pdf' if 'pdf' in doc.file.name else 'image/jpeg'

    response = HttpResponse(doc.file.read(), content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename={}'.format(doc.filename)

    return response