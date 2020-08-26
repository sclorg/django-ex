from django.shortcuts import render
from django.views.generic.edit import FormView
from django import forms

from ..validators import file_scan_validation

"""
Everything in this file is considered as proof of concept work and should not be used for production code.
"""


class UploadForm(forms.Form):
    upload_file = forms.FileField(validators=[file_scan_validation])


class UploadScan(FormView):
    form_class = UploadForm
    template_name = "poc/upload.html"

    def form_valid(self, form):
        context = self.get_context_data()
        context['validation_success'] = True
        return render(self.request, self.template_name, context)
