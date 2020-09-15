#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    from django.core.management import execute_from_command_line

    # check if the app is running on OpenShift
    if not os.environ.get('OPENSHIFT_BUILD_NAMESPACE', False):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.local")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.openshift")

        # run 'npm_build' (custom management command) when collectstatic is called in 
        # the S2I assemble script
        if sys.argv[1] == 'collectstatic':
            execute_from_command_line(['manage.py','npm_build'])

        # run 'loaddata' before running the migrations
        if sys.argv[1] == 'migrate':
            execute_from_command_line(['manage.py', 'loaddata', '/opt/app-root/src/edivorce/fixtures/Question.json'])

    execute_from_command_line(sys.argv)
