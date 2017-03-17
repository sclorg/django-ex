"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

# check if the app is running on OpenShift
if not os.environ.get('OPENSHIFT_BUILD_NAMESPACE', False):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.local")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.openshift")

    if os.environ.get('POD_INIT_COMPLETE', "") != "True":
        # compress the static assets
        execute_from_command_line(['manage.py', 'compress', '--force'])
        # load the Question fixture
        execute_from_command_line(['manage.py', 'loaddata', '/opt/app-root/src/edivorce/fixtures/Question.json'])

        os.environ["POD_INIT_COMPLETE"] = "True"

application = get_wsgi_application()
