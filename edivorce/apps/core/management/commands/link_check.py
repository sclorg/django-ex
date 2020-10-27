import os
import sys
from urllib.request import urlopen

from bs4 import BeautifulSoup

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Checks links in the eDivorce application.'

    def _check_link(self, address):
        try:
            resp = urlopen(address) # nosec - This is for internal use only to check for broken links.
            if resp.status in [400, 404, 403, 408, 409, 501, 502, 503]:
                return f"{resp.status} - {resp.reason}"
        except Exception as e:
            return f"{e}"
        return None

    def handle(self, *args, **options):
        errors = []

        for root, directory, files in os.walk(settings.BASE_DIR + '/apps/core/templates/'):
            for file in files:
                if '.html' in file:
                    file_path = os.path.join(root, file)

                    fs = open(file_path)

                    print('Parsing: ' + fs.name)

                    soup = BeautifulSoup(fs, 'html.parser')
                    links = soup.find_all('a', href=True)
                    for link in links:
                        if link is None:
                            continue
                        if link['href'].startswith('http'):
                            filename = str(fs.name)

                            status = self._check_link(link['href'])
                            if status:
                                errors.append({
                                    'link': link['href'],
                                    'error': status,
                                    'file': filename
                                })

        if len(errors) > 0:
            for error in errors:
                print('-------------------------------------------------------------')
                print(f'File: {error["file"]}')
                print(f'link: {error["link"]}')
                print(f'Error: {error["error"]}\r\n')
            sys.exit(1)
