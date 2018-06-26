"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import platform
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line
    
# check if the app is running on OpenShift
if not os.environ.get('OPENSHIFT_BUILD_NAMESPACE', False):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.local")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.openshift")

    if os.environ.get('POD_INIT_COMPLETE', "") != "True":
        # gunicorn starts multiple threads and runs wsgi.py once for each thread.  We only want
        # these commands to run ONCE.
        os.environ["POD_INIT_COMPLETE"] = "True"
        # compress the static assets
        execute_from_command_line(['manage.py', 'compress', '--force'])


question_fixture_path = '/opt/app-root/src/edivorce/fixtures/Question.json'
platform_name = platform.system()
if platform_name == "Windows":
    question_fixture_path = os.path.realpath("./edivorce/fixtures/Question.json")

# load the Question fixture
execute_from_command_line(['manage.py', 'loaddata', question_fixture_path])

application = get_wsgi_application()
