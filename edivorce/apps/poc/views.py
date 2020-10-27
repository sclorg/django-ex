import logging

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView, CreateView, DeleteView
from django import forms
from django.http import HttpResponse
from django.conf import settings

from edivorce.apps.core.utils.efiling_submission import EFilingSubmission
from edivorce.apps.core.utils.efiling_packaging import PACKAGE_PARTY_FORMAT
from edivorce.apps.core.validators import file_scan_validation
from edivorce.apps.core.models import Document

logger = logging.getLogger(__name__)

"""
Everything in this file is considered as proof of concept work and should not be used for production code.
"""


class UploadScanForm(forms.Form):
    upload_file = forms.FileField(validators=[file_scan_validation])


class MultipleUploadForm(forms.Form):
    upload_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class UploadScan(FormView):
    form_class = UploadScanForm
    template_name = "scan.html"

    def form_valid(self, form):
        context = self.get_context_data()
        context['validation_success'] = True
        return render(self.request, self.template_name, context)


class UploadStorage(CreateView):
    model = Document
    fields = ['file', 'doc_type', 'party_code']
    template_name = "storage.html"
    success_url = settings.FORCE_SCRIPT_NAME + 'poc/storage'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UploadStorage, self).dispatch(request, *args, **kwargs)  

    def get_context_data(self, **kwargs):
        kwargs['documents'] = Document.objects.all()
        return super(UploadStorage, self).get_context_data(**kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.bceid_user = self.request.user
        return super(UploadStorage, self).form_valid(form)


class UploadStorageDelete(DeleteView):
    model = Document
    success_url = settings.FORCE_SCRIPT_NAME + 'poc/storage'
    template_name = 'poc/document_confirm_delete.html'


def view_document_file(request, document_id):
    doc = Document.objects.get(id=document_id)

    content_type = 'application/pdf' if 'pdf' in doc.file.name else 'image/jpeg'

    response = HttpResponse(doc.file.read(), content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename={}'.format(doc.filename)

    return response


class EFilingSubmissionUpload(FormView):
    form_class = MultipleUploadForm
    template_name = 'hub.html'
    success_url = '/poc/hub'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('upload_file')
        if form.is_valid():
            # NOTE: this does not do any validation for file types .. make sure that is done
            # prior to sending to eFiling Hub
            post_files = []
            if files:
                for file in files:
                    post_files.append(('files', (file.name, file.read())))

            # generate the list of parties to send to eFiling Hub
            parties = []
            for i in range(0, 2):
                party = PACKAGE_PARTY_FORMAT.copy()
                party['firstName'] = 'Party {}'.format(i)
                party['lastName'] = 'Test'
                parties.append(party)

            hub = EFilingSubmission(initial_filing=True)
            redirect, msg = hub.upload(request, post_files, parties=parties)
            if redirect:
                self.success_url = redirect

                return self.form_valid(form)

            form.add_error('upload_file', msg)

        return self.form_invalid(form)
