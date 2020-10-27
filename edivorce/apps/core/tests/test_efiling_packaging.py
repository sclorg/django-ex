import json
from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.test import TransactionTestCase
from django.test.client import RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile

from edivorce.apps.core.utils.efiling_submission import EFilingSubmission
from edivorce.apps.core.utils.efiling_packaging import EFilingPackaging, PACKAGE_PARTY_FORMAT, PACKAGE_DOCUMENT_FORMAT


class EFilingPackagingTests(TransactionTestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

        self.request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()

        self.packaging = EFilingPackaging(initial_filing=True)

    def test_format_package(self):
        files = []
        documents = []
        for i in range(0, 2):
            document = PACKAGE_DOCUMENT_FORMAT.copy()
            filename = 'form_{}.pdf'.format(i)
            document['name'] = filename
            file = SimpleUploadedFile(filename, b'test content')
            files.append(('files', (file.name, file.read())))
            documents.append(document)
        parties = []
        for i in range(0, 2):
            party = PACKAGE_PARTY_FORMAT.copy()
            party['firstName'] = 'Party {}'.format(i)
            party['lastName'] = 'Test'
            parties.append(party)

        location = '6011'
        package = self.packaging.format_package(self.request, files, documents, parties, location)

        self.assertTrue(package)
        self.assertEqual(package['filingPackage']['documents'][0]['name'], 'form_0.pdf')
        self.assertEqual(package['filingPackage']['documents'][1]['name'], 'form_1.pdf')
        self.assertEqual(package['filingPackage']['parties'][0]['firstName'], 'Party 0')
        self.assertEqual(package['filingPackage']['parties'][1]['firstName'], 'Party 1')
