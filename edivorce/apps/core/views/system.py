from django.http import HttpResponse
from edivorce.apps.core.models import Question


def health(request):
    """
    OpenShift health check
    """
    return HttpResponse(Question.objects.count())
