from django.http import HttpResponse
from django.db import connection


def health(request):
    """View to check server health"""
    return HttpResponse()
