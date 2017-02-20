#!/usr/bin/env python

# NOTE: this isn't a real setup.py file.  It has been added here
# so additional steps could be injected into the OpenShift/Docker S2I build.
#
# If a file called "setup.py" exists, then the S2I assemble script will run it
# during the build.
#
# TODO: I have added Django-Compressor code to wsgi.py so it runs during deployment
#       instead. I'm just keeping the code here until I am sure the other approach
#       is working.  This script currently does NOTHING

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edivorce.settings.openshift")
from django.core.management import execute_from_command_line

print('')
print('NOTICE: THIS SCRIPT DOES NOT SET UP THE PROJECT!!')
print('If you are trying to set up the project, please run the following command instead:')
print('$ pip install -r requirements.txt')
print('')
print('Executing additional OpenShift S2I assemble tasks defined in setup.py')
print('')

# Run Django-Compressor offline compression
# print('Running Django Compressor offline compression')
# execute_from_command_line(['manage.py', 'compress'])
