#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    # check if the app is running on OpenShift
    if not os.environ.get('OPENSHIFT_BUILD_NAMESPACE', False):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.local")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.openshift")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
