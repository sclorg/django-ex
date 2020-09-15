import json
import requests
import logging
import uuid

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse

logger = logging.getLogger(__name__)

PACKAGE_DOCUMENT_FORMAT = {
    "name": "string",
    "type": "WNC",
    "isAmendment": "false",
    "isSupremeCourtScheduling": "false",
    "data": {},
    "md5": "string"
}

PACKAGE_PARTY_FORMAT = {
    "partyType": "IND",
    "roleType": "CLA",
    "firstName": "",
    "middleName": "",
    "lastName": "",
}

PACKAGE_FORMAT = {
    "clientAppName": "Online Divorce Assistant",
    "filingPackage": {
        "documents": [],
        "court": {
            "location": "1211",
            "level": "P",
            "courtClass": "F",
            "division": "I",
            "fileNumber": "1234",
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


class EFilingHub:

    def __init__(self):
        self.client_id = settings.EFILING_HUB_CLIENT_ID
        self.client_secret = settings.EFILING_HUB_CLIENT_SECRET
        self.token_base_url = settings.EFILING_HUB_TOKEN_BASE_URL
        self.token_realm = settings.EFILING_HUB_REALM
        self.api_base_url = settings.EFILING_HUB_API_BASE_URL

        self.submission_id = None

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
                username = request.session.get('login_name', None)
                if username:
                    if username in settings.EFILING_BCEID:
                        return settings.EFILING_BCEID[username]
                return request.session.get('fake_bceid_guid', None)
            return request.session.get('smgov_userguid', None)

        guid = _get_raw_bceid(request)
        if guid:
            return str(uuid.UUID(guid))
        return guid

    def _format_package(self, request, files, parties):
        documents = []
        for file in files:
            document = PACKAGE_DOCUMENT_FORMAT.copy()
            document['name'] = file[1][0]
            documents.append(document)
        package = PACKAGE_FORMAT.copy()
        package['filingPackage']['documents'] = documents
        if parties:
            package['filingPackage']['parties'] = parties
        # update return urls
        package['navigationUrls']['success'] = request.build_absolute_uri(
            reverse('dashboard_nav', args=['check_with_registry']))
        package['navigationUrls']['error'] = request.build_absolute_uri(
            reverse('dashboard_nav', args=['check_with_registry']))
        package['navigationUrls']['cancel'] = request.build_absolute_uri(
            reverse('dashboard_nav', args=['check_with_registry']))

        return package

    # -- EFILING HUB INTERFACE --

    def upload(self, request, files, parties=None):
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

        response = self._get_api(request, f'{self.api_base_url}/submission/documents', transaction_id, bce_id,
                                 headers={}, files=files)
        if response.status_code == 200:
            response = json.loads(response.text)

            if "submissionId" in response and response['submissionId'] != "":
                # get the redirect url
                headers = {
                    'Content-Type': 'application/json'
                }
                package_data = self._format_package(request, files, parties=parties)
                url = f"{self.api_base_url}/submission/{response['submissionId']}/generateUrl"
                response = self._get_api(request, url, transaction_id, bce_id, headers=headers,
                                         data=json.dumps(package_data))

                if response.status_code == 200:
                    response = json.loads(response.text)
                    return response['efilingUrl'], 'success'

                response = json.loads(response.text)

                return None, f"{response['error']} - {response['message']}"

        return None, f'{response.status_code} - {response.text}'
