import os

from django.contrib.staticfiles.management.commands.runserver import (
    Command as NpmBuildCommand,
)

class Command(NpmBuildCommand):

    def run(self, **options):
        os.system("npm --prefix /opt/app-root/src/vue install /opt/app-root/src/vue --loglevel info")
        os.system("npm --prefix /opt/app-root/src/vue run build")        