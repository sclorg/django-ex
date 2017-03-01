from django.http import HttpResponse
from django.shortcuts import render

from edivorce.apps.core.models import Question


def health(request):
    """
    OpenShift health check
    """
    return HttpResponse(Question.objects.count())

def headers(request):
    return render(request, 'localdev/debug.html')