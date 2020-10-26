import datetime
import hashlib
import json
import logging
import re
import requests
import uuid

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from edivorce.apps.core.models import Document
from edivorce.apps.core.utils.question_step_mapping import list_of_registries
from edivorce.apps.core.views.pdf import images_to_pdf, pdf_form

logger = logging.getLogger(__name__)

PACKAGE_DOCUMENT_FORMAT = {
    "name": "string",
    "type": "AFDO",
    "isAmendment": "false",
    "isSupremeCourtScheduling": "false",
    "data": {},
    "md5": "string"
}

PACKAGE_PARTY_FORMAT = {
    "partyType": "IND",
    "roleType": "CLA",
    "firstName": "FirstName",
    "middleName": "",
    "lastName": "LastName",
}

PACKAGE_FORMAT = {
    "clientAppName": "Online Divorce Assistant",
    "filingPackage": {
        "documents": [],
        "court": {
            "location": "4801",
            "level": "S",
            "courtClass": "E",
            "division": "I",
            "participatingClass": "string"
        },
        "parties": []
    },
    "navigationUrls": {
        "success": "string",
        "error": "string",
        "cancel": "string"
    }
}

NJF_ALIAS_FORMAT = {
    "nameType": "AKA",
    "surname": "",
    "given1": "",
    "given2": "",
    "given3": ""
}

NJF_JSON_FORMAT = {
    "parties": [
        {
            "label": "Claimant 1",
            "surname": "",
            "given1": "",
            "given2": "",
            "given3": "",
            "birthDate": "",
            "email": "",
            "aliases": [],
            "surnameAtBirth": "",
            "surnameBeforeMarriage": "",
            "signingVirtually": False
        },
        {
            "label": "Claimant 2",
            "surname": "",
            "given1": "",
            "given2": "",
            "given3": "",
            "birthDate": "",
            "email": "",
            "aliases": [],
            "surnameAtBirth": "",
            "surnameBeforeMarriage": "",
            "signingVirtually": False
        }
    ],
    "placeOfMarriage": {
        "country": "",
        "province": "",
        "city": ""
    },
    "dateOfMarriage": "",
    "reasonForDivorce": "S",
    "childSupportAct": [],
    "spouseSupportAct": "",
    "ordersSought": []
}


class EFilingHub:

    def __init__(self, initial_filing):
        self.client_id = settings.EFILING_HUB_CLIENT_ID
        self.client_secret = settings.EFILING_HUB_CLIENT_SECRET
        self.token_base_url = settings.EFILING_HUB_TOKEN_BASE_URL
        self.token_realm = settings.EFILING_HUB_REALM
        self.api_base_url = settings.EFILING_HUB_API_BASE_URL

        self.submission_id = None
        self.initial_filing = initial_filing

    def _get_token(self, request):
        payload = f'client_id={self.client_id}&grant_type=client_credentials&client_secret={self.client_secret}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        url = f'{self.token_base_url}/auth/realms/{self.token_realm}/protocol/openid-connect/token'

        response = requests.post(url, headers=headers, data=payload)
        logging.debug(f'EFH - Get Token {response.status_code}')
        if response.status_code == 200:
            response = json.loads(response.text)

            # save in session .. lets just assume that current user is authenticated
            if 'access_token' in response:
                request.session['access_token'] = response['access_token']
                if 'refresh_token' in response:
                    request.session['refresh_token'] = response['refresh_token']

                return True
        return False

    def _refresh_token(self, request):
        refresh_token = request.session.get('refresh_token', None)
        if not refresh_token:
            return False

        payload = f'client_id={self.client_id}&grant_type=refresh_token&client_secret={self.client_secret}&refresh_token={refresh_token}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        url = f'{self.token_base_url}/auth/realms/{self.token_realm}/protocol/openid-connect/token'

        response = requests.post(url, headers=headers, data=payload)
        logging.debug(f'EFH - Get Refresh Token {response.status_code}')

        response = json.loads(response.text)

        # save in session .. lets just assume that current user is authenticated
        if 'access_token' in response:
            request.session['access_token'] = response['access_token']
            if 'refresh_token' in response:
                request.session['refresh_token'] = response['refresh_token']

            return True
        return False

    def _get_api(self, request, url, transaction_id, bce_id, headers, data=None, files=None):
        # make sure we have a session
        access_token = request.session.get('access_token', None)
        if not access_token:
            if not self._get_token(request):
                raise Exception('EFH - Unable to get API Token')

        access_token = request.session.get('access_token', None)
        headers.update({
            'X-Transaction-Id': transaction_id,
            'X-User-Id': bce_id,
            'Authorization': f'Bearer {access_token}'
        })

        if not data:
            data = {}

        response = requests.post(url, headers=headers, data=data, files=files)
        logging.debug(f'EFH - Get API {response.status_code} {response.text}')

        if response.status_code == 401:
            # not authorized .. try refreshing token
            if self._refresh_token(request):
                access_token = request.session.get('access_token', None)
                headers.update({
                    'X-Transaction-Id': transaction_id,
                    'X-User-Id': bce_id,
                    'Authorization': f'Bearer {access_token}'
                })

                response = requests.post(url, headers=headers, data=data, files=files)
                logging.debug(f'EFH - Get API Retry {response.status_code} {response.text}')

        return response

    def _get_transaction(self, request):
        """
        Get the current transaction id stored in session, otherwise generate one.
        :param request:
        :return:
        """
        guid = request.session.get('transaction_id', None)
        if not guid:
            guid = str(uuid.uuid4())
            request.session['transaction_id'] = guid
        return guid

    def _get_bceid(self, request):

        def _get_raw_bceid(request):
            is_localdev = settings.DEPLOYMENT_TYPE in ['localdev', 'minishift']
            if is_localdev:
                # to integrate with the Test eFiling Hub, we need a valid BCEID which is
                # unavailable for a local eDivorce environment. Use an env specified mapping
                # to figure out what we should pass through to eFiling Hub. This BCEID username
                # needs to match with what you will be logging in with to the Test BCEID environment.
                return settings.EFILING_BCEID
            return request.session.get('bcgov_userguid', None)

        guid = _get_raw_bceid(request)
        if guid:
            return str(uuid.UUID(guid))
        return guid

    def _format_package(self, request, files, documents, parties, location):
        package = PACKAGE_FORMAT.copy()
        package['filingPackage']['court']['location'] = location
        package['filingPackage']['documents'] = documents
        if parties:
            package['filingPackage']['parties'] = parties
        # update return urls
        if self.initial_filing:
            package['navigationUrls']['error'] = request.build_absolute_uri(
                reverse('dashboard_nav', args=['initial_filing']))
            package['navigationUrls']['cancel'] = request.build_absolute_uri(
                reverse('dashboard_nav', args=['initial_filing'])) + '?cancelled=1'
            package['navigationUrls']['success'] = request.build_absolute_uri(
                reverse('after_submit_initial_files'))
        else:
            package['navigationUrls']['error'] = request.build_absolute_uri(
                reverse('dashboard_nav', args=['final_filing']))
            package['navigationUrls']['cancel'] = request.build_absolute_uri(
                reverse('dashboard_nav', args=['final_filing'])) + '?cancelled=1'
            package['navigationUrls']['success'] = request.build_absolute_uri(
                reverse('after_submit_final_files'))

        return package

    def _get_document(self, doc_type, party_code):
        document = PACKAGE_DOCUMENT_FORMAT.copy()
        filename = self._get_filename(doc_type, party_code)
        document['name'] = filename
        document['type'] = doc_type
        return document

    def _get_filename(self, doc_type, party_code):
        form_name = Document.form_types[doc_type]
        slug = re.sub('[^0-9a-zA-Z]+', '-', form_name).strip('-')
        if party_code == 0:
            return slug + ".pdf"
        elif party_code == 1:
            return slug + "--Claimant1.pdf"
        else:
            return slug + "--Claimant2.pdf"

    def _get_json_data(self, responses):

        def format_date(str):
            try:
                return datetime.datetime.strptime(str, '%b %d, %Y').strftime('%Y-%m-%d')
            except:
                return ''

        def get_aliases(str):
            aliases = []
            names = json.loads(str)
            for name in names:
                if len(name) == 5 and name[1] != '' and name[2] != '':
                    alias = NJF_ALIAS_FORMAT.copy()
                    alias["surname"] = name[1]
                    alias["given1"] = name[2]
                    alias["given2"] = name[3]
                    alias["given3"] = name[4]
                    aliases.append(alias)
            return aliases

        r = responses
        d = NJF_JSON_FORMAT.copy()

        signing_location_you = ''
        signing_location_spouse = ''

        if r.get('how_to_sign') == 'Together':
            signing_location_you = r.get('signing_location')
            signing_location_spouse = r.get('signing_location')
        elif r.get('how_to_sign') == 'Separately':
            signing_location_you = r.get('signing_location_you')
            signing_location_spouse = r.get('signing_location_spouse')

        party1 = d["parties"][0]
        party1["surname"] = r.get('last_name_you', '')
        party1["given1"] = r.get('given_name_1_you', '')
        party1["given2"] = r.get('given_name_2_you', '')
        party1["given3"] = r.get('given_name_3_you', '')
        party1["birthDate"] = format_date(r.get('birthday_you'))
        party1["surnameAtBirth"] = r.get('last_name_born_you', '')
        party1["surnameBeforeMarriage"] = r.get('last_name_before_married_you', '')
        email = r.get('email_you', '')
        if not email:
            email = r.get('address_to_send_official_document_email_you', '')
        party1["email"] = email
        party1["signingVirtually"] = signing_location_you == 'Virtual'
        if r.get('any_other_name_you') == 'YES':
            party1["aliases"] = get_aliases(r.get('other_name_you'))

        party2 = d["parties"][1]
        party2["surname"] = r.get('last_name_spouse', '')
        party2["given1"] = r.get('given_name_1_spouse', '')
        party2["given2"] = r.get('given_name_2_spouse', '')
        party2["given3"] = r.get('given_name_3_spouse', '')
        party2["birthDate"] = format_date(r.get('birthday_spouse'))
        party2["surnameAtBirth"] = r.get('last_name_born_spouse', '')
        party2["surnameBeforeMarriage"] = r.get('last_name_before_married_spouse', '')
        email = r.get('email_spouse', '')
        if not email:
            email = r.get('address_to_send_official_document_email_spouse', '')
        party2["email"] = email
        party2["signingVirtually"] = signing_location_spouse == 'Virtual'
        if r.get('any_other_name_spouse') == 'YES':
            party2["aliases"] = get_aliases(r.get('other_name_spouse'))

        d["dateOfMarriage"] = format_date(r.get('when_were_you_married'))
        d["placeOfMarriage"]["country"] = r.get('where_were_you_married_country', '')
        d["placeOfMarriage"]["province"] = r.get('where_were_you_married_prov', '')
        d["placeOfMarriage"]["city"] = r.get('where_were_you_married_city', '')

        d["childSupportAct"] = json.loads(r.get('child_support_act', '[]'))
        d["spouseSupportAct"] = r.get('spouse_support_act', '')

        orders_sought = json.loads(r.get('want_which_orders', '[]'))

        if 'A legal end to the marriage' in orders_sought:
            d["ordersSought"].append('DIV')

        if 'Spousal support' in orders_sought:
            d["ordersSought"].append('SSU')

        if 'Division of property and debts' in orders_sought:
            division = r.get('deal_with_property_debt', '')
            if division == 'Equal division':
                d["ordersSought"].append('DFA')
            if division == 'Unequal division':
                d["ordersSought"].append('RFA')
            if re.sub(r'\W+', '', r.get('other_property_claims', '')) != '':
                d["ordersSought"].append('PRO')

        if 'Child support' in orders_sought:
            d["ordersSought"].append('CSU')

        if 'Other orders' in orders_sought:
            if r.get('name_change_you') == 'YES' or r.get('name_change_spouse') == 'YES':
                d["ordersSought"].append('NAM')
            if re.sub(r'\W+', '', r.get('other_orders_detail ', '')) != '':
                d["ordersSought"].append('OTH')

        return d

    # -- EFILING HUB INTERFACE --
    def get_files(self, request, responses, uploaded, generated):

        post_files = []
        documents = []

        for form in generated:
            doc_type = form['doc_type']
            document = self._get_document(doc_type, 0)
            if doc_type == 'NJF':
                document['data'] = self._get_json_data(responses)
            pdf_response = pdf_form(request, str(form['form_number']))
            document['md5'] = hashlib.md5(pdf_response.content).hexdigest()
            post_files.append(('files', (document['name'], pdf_response.content)))
            documents.append(document)

        for form in uploaded:
            party_code = form['party_code']
            doc_type = form['doc_type']
            pdf_response = images_to_pdf(request, doc_type, party_code)
            if pdf_response.status_code == 200:
                document = self._get_document(doc_type, party_code)
                document['md5'] = hashlib.md5(pdf_response.content).hexdigest()
                post_files.append(('files', (document['name'], pdf_response.content)))
                documents.append(document)

        return post_files, documents

    def get_parties(self, responses):

        # generate the list of parties to send to eFiling Hub
        parties = []

        party1 = PACKAGE_PARTY_FORMAT.copy()
        party1['firstName'] = responses.get('given_name_1_you', '')
        party1['middleName'] = (responses.get('given_name_2_you', '') +
                                ' ' +
                                responses.get('given_name_3_you', '')).strip()
        party1['lastName'] = responses.get('last_name_you', '')
        parties.append(party1)

        party2 = PACKAGE_PARTY_FORMAT.copy()
        party2['firstName'] = responses.get('given_name_1_spouse', '')
        party2['middleName'] = (responses.get('given_name_2_spouse', '') +
                                ' ' +
                                responses.get('given_name_3_spouse', '')).strip()
        party2['lastName'] = responses.get('last_name_spouse', '')
        parties.append(party2)

        return parties

    def get_location(self, responses):
        location_name = responses.get('court_registry_for_filing', '')
        return list_of_registries.get(location_name, '0000')

    def upload(self, request, files, documents=None, parties=None, location=None):
        """
        Does an initial upload of documents and gets the generated eFiling Hub url.
        :param parties:
        :param request:
        :param files: Files need to be a list of tuples in the form ('files': (filename, filecontent))
        :return: The url for redirect and any error messages
        """
        # Find the transaction id .. this will be a unique guid generated by eDivorce thats passed to Efiling Hub. We
        # will tie it to the session.

        transaction_id = self._get_transaction(request)
        bce_id = self._get_bceid(request)

        # if bce_id is None .. we basically have an anonymous user so raise an error
        if bce_id is None:
            raise PermissionDenied()

        # package_data, files = self._get_data(request, responses, uploaded, generated)

        url = f'{self.api_base_url}/submission/documents'
        response = self._get_api(request, url, transaction_id, bce_id, headers={}, files=files)
        if response.status_code == 200:
            response = json.loads(response.text)

            if "submissionId" in response and response['submissionId'] != "":
                # get the redirect url
                headers = {
                    'Content-Type': 'application/json'
                }
                package_data = self._format_package(request, files, documents, parties, location)
                url = f"{self.api_base_url}/submission/{response['submissionId']}/generateUrl"
                data = json.dumps(package_data)
                response = self._get_api(request, url, transaction_id, bce_id, headers, data)

                if response.status_code == 200:
                    response = json.loads(response.text)
                    return response['efilingUrl'], 'success'

                response = json.loads(response.text)

                return None, f"{response['error']} - {response['message']}"

        return None, f'{response.status_code} - {response.text}'
