import os
from django.shortcuts import render

from .models import PageView

# Create your views here.

def index(request):
    hostname = os.getenv('HOSTNAME', 'unknown')
    PageView.objects.create(hostname=hostname)
    return render(request, 'openshift/index.html', {
        'hostname': hostname,
        'count': PageView.objects.count()
    })
