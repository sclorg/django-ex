import os
from django.shortcuts import render
from django.conf import settings

from .models import PageView

# Create your views here.


def _database_info():
    db_settings = settings.DATABASES['default']
    if 'postgres' in db_settings['ENGINE']:
        engine = 'PostgreSQL'
        info = '{HOST}:{PORT}/{NAME}'.format(**db_settings)
    else:
        engine = 'SQLite'
        info = '{NAME}'.format(**db_settings)
    return '{} ({})'.format(engine, info)

database_info = _database_info()


def index(request):
    hostname = os.getenv('HOSTNAME', 'unknown')
    PageView.objects.create(hostname=hostname)

    return render(request, 'welcome/index.html', {
        'hostname': hostname,
        'database_info': database_info,
        'count': PageView.objects.count()
    })
