#!/usr/bin/env python
import os
import sys
import decouple

if __name__ == "__main__":

    if decouple.config("LOCAL_DEV", default=False, cast=bool):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.local")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.openshift")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
