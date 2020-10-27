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

    def test_get_location_success(self):
        responses = {
            "court_registry_for_filing": "Vancouver"
        }
        location = self.packaging.get_location(responses)
        self.assertEqual(location, '6011')

    def test_get_location_fail(self):
        responses = {
            "court_registry_for_filing": "Tokyo"
        }
        location = self.packaging.get_location(responses)
        self.assertEqual(location, '0000')

        responses = {}
        location = self.packaging.get_location(responses)
        self.assertEqual(location, '0000')

    def test_get_json_data_signing_location(self):

        responses = {
            'how_to_sign': 'Together',
            'signing_location': 'Virtual'
        }

        json = self.packaging._get_json_data(responses)

        self.assertEqual(json['parties'][0]["signingVirtually"], True)
        self.assertEqual(json['parties'][1]["signingVirtually"], True)

        responses = {
            'how_to_sign': 'Separately',
            'signing_location_you': 'Virtual',
            'signing_location_spouse': 'In-person'
        }

        json = self.packaging._get_json_data(responses)

        self.assertEqual(json['parties'][0]["signingVirtually"], True)
        self.assertEqual(json['parties'][1]["signingVirtually"], False)

    def test_get_json_data_parties(self):

        responses = {
            'last_name_you': 'Smith',
            'given_name_1_you': 'John',
            'given_name_2_you': 'Jonas',
            'given_name_3_you': '',
            'birthday_you': 'Jun 1, 1970',
            'last_name_before_married_you': 'Baker',
            'last_name_born_you': '',
            'email_you': 'you@gmail.com',
            'address_to_send_official_document_email_you': 'you2@gmail.com',
            'last_name_spouse': 'Jones',
            'given_name_1_spouse': 'Jane',
            'given_name_2_spouse': 'Jennifer',
            'given_name_3_spouse': 'Janet',
            'birthday_spouse': 'Jan 15, 1980',
            'last_name_before_married_spouse': 'Wilson',
            'last_name_born_spouse': 'Ross',
            'email_spouse': '',
            'address_to_send_official_document_email_spouse': 'spouse2@gmail.com',
        }

        json = self.packaging._get_json_data(responses)

        self.assertEqual(json['parties'][0]['surname'], 'Smith')
        self.assertEqual(json['parties'][0]['given1'], 'John')
        self.assertEqual(json['parties'][0]['given2'], 'Jonas')
        self.assertEqual(json['parties'][0]['given3'], '')
        self.assertEqual(json['parties'][0]['birthDate'], '1970-06-01')
        self.assertEqual(json['parties'][0]['surnameBeforeMarriage'], 'Baker')
        self.assertEqual(json['parties'][0]['surnameAtBirth'], '')
        self.assertEqual(json['parties'][0]['email'], 'you@gmail.com')

        self.assertEqual(json['parties'][1]['surname'], 'Jones')
        self.assertEqual(json['parties'][1]['given1'], 'Jane')
        self.assertEqual(json['parties'][1]['given2'], 'Jennifer')
        self.assertEqual(json['parties'][1]['given3'], 'Janet')
        self.assertEqual(json['parties'][1]['birthDate'], '1980-01-15')
        self.assertEqual(json['parties'][1]['surnameBeforeMarriage'], 'Wilson')
        self.assertEqual(json['parties'][1]['surnameAtBirth'], 'Ross')
        self.assertEqual(json['parties'][1]['email'], 'spouse2@gmail.com')

    def test_get_json_data_aliases(self):

        responses = {
            'any_other_name_you': 'YES',
            'other_name_you': '[["also known as","Smith","Mike","Joe","Skippy"],["also known as","D","A","B","C"]]',
            'any_other_name_spouse': 'NO'
        }

        json = self.packaging._get_json_data(responses)

        self.assertEqual(json['parties'][0]["aliases"][0]["surname"], "Smith")
        self.assertEqual(json['parties'][0]["aliases"][0]["given1"], "Mike")
        self.assertEqual(json['parties'][0]["aliases"][0]["given2"], "Joe")
        self.assertEqual(json['parties'][0]["aliases"][0]["given3"], "Skippy")
        self.assertEqual(json['parties'][0]["aliases"][1]["surname"], "D")
        self.assertEqual(len(json['parties'][1]["aliases"]), 0)
