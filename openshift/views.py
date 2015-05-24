import os
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'openshift/index.html', {'HOSTNAME': os.getenv('HOSTNAME', 'unknown')})
