import json
import logging
import requests
import uuid

from django.conf import settings
from django.core.exceptions import PermissionDenied

from .efiling_packaging import EFilingPackaging

logger = logging.getLogger(__name__)


class EFilingSubmission:

    def __init__(self, initial_filing):
        self.client_id = settings.EFILING_HUB_KEYCLOAK_CLIENT_ID
        self.client_secret = settings.EFILING_HUB_KEYCLOAK_SECRET
        self.token_base_url = settings.EFILING_HUB_KEYCLOAK_BASE_URL
        self.token_realm = settings.EFILING_HUB_KEYCLOAK_REALM
        self.api_base_url = settings.EFILING_HUB_API_BASE_URL
        self.initial_filing = initial_filing
        self.packaging = EFilingPackaging(initial_filing)
        self.submission_id = None
        self.access_token = None
        self.refresh_token = None

    def _get_token(self, request):
        payload = f'client_id={self.client_id}&grant_type=client_credentials&client_secret={self.client_secret}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        url = f'{self.token_base_url}/auth/realms/{self.token_realm}/protocol/openid-connect/token'

        response = requests.post(url, headers=headers, data=payload)
        logging.debug(f'EFH - Get Token {response.status_code}')
        if response.status_code == 200:
            response = json.loads(response.text)

            # save token as object property..
            if 'access_token' in response:
                self.access_token = response['access_token']
                if 'refresh_token' in response:
                    self.refresh_token = response['refresh_token']

                return True
        return False

    def _refresh_token(self, request):
        if not self.refresh_token:
            return False

        payload = f'client_id={self.client_id}&grant_type=refresh_token&client_secret={self.client_secret}&refresh_token={self.refresh_token}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        url = f'{self.token_base_url}/auth/realms/{self.token_realm}/protocol/openid-connect/token'

        response = requests.post(url, headers=headers, data=payload)
        logging.debug(f'EFH - Get Refresh Token {response.status_code}')

        response = json.loads(response.text)

        # save in session .. lets just assume that current user is authenticated
        if 'access_token' in response:
            self.access_token = response['access_token']
            if 'refresh_token' in response:
                self.refresh_token = response['refresh_token']

            return True
        return False

    def _get_api(self, request, url, transaction_id, bce_id, headers, data=None, files=None):
        # make sure we have an access token
        if not self.access_token:
            if not self._get_token(request):
                raise Exception('EFH - Unable to get API Token')

        headers.update({
            'X-Transaction-Id': transaction_id,
            'X-User-Id': bce_id,
            'Authorization': f'Bearer {self.access_token}'
        })

        if not data:
            data = {}

        response = requests.post(url, headers=headers, data=data, files=files)
        logging.debug(f'EFH - Get API {response.status_code} {response.text}')

        if response.status_code == 401:
            # not authorized .. try refreshing token
            if self._refresh_token(request):
                headers.update({
                    'X-Transaction-Id': transaction_id,
                    'X-User-Id': bce_id,
                    'Authorization': f'Bearer {self.access_token}'
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
            if settings.DEPLOYMENT_TYPE == 'localdev':
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

    def upload(self, request, responses, files, documents=None, parties=None):
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

        url = f'{self.api_base_url}/submission/documents'
        print('DEBUG: ' + url)
        response = self._get_api(request, url, transaction_id, bce_id, headers={}, files=files)
        if response.status_code == 200:
            response = json.loads(response.text)

            if "submissionId" in response and response['submissionId'] != "":
                # get the redirect url
                headers = {
                    'Content-Type': 'application/json'
                }
                package_data = self.packaging.format_package(request, responses, files, documents)
                url = f"{self.api_base_url}/submission/{response['submissionId']}/generateUrl"
                print('DEBUG: ' + url)
                data = json.dumps(package_data)
                print('DEBUG: ' + data)
                response = self._get_api(request, url, transaction_id, bce_id, headers, data)

                if response.status_code == 200:
                    response = json.loads(response.text)
                    return response['efilingUrl'], 'success'

                response = json.loads(response.text)

                if 'details' in response and len(response['details']) > 0:
                    message = f"<p>{response['message']}</p>"
                    details = f"<ul><li>{'</li><li>'.join(response['details'])}</li></ul>"
                    return None, message + details

                return None, f"{response['error']} - {response['message']}"

        if response.status_code == 401:
            print(response.headers.get('WWW-Authenticate', ''))
            return None, '401 - Authentication Failed'

        return None, f'{response.status_code} - {response.text}'
