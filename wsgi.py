"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import decouple
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

if decouple.config("LOCAL_DEV", default=False, cast=bool):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.local")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.openshift")
    execute_from_command_line(['manage.py', 'compress', '--force'])

application = get_wsgi_application()
