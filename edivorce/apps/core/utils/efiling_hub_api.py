import json
import logging
import requests
import uuid

from django.conf import settings
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


class EFilingHubApi:

    def __init__(self):
        self.client_id = settings.EFILING_HUB_KEYCLOAK_CLIENT_ID
        self.client_secret = settings.EFILING_HUB_KEYCLOAK_SECRET
        self.token_base_url = settings.EFILING_HUB_KEYCLOAK_BASE_URL
        self.token_realm = settings.EFILING_HUB_KEYCLOAK_REALM
        self.api_base_url = settings.EFILING_HUB_API_BASE_URL
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

    def _set_headers(self, headers, bceid_guid, access_token, transaction_id=None):
        if transaction_id:
            headers.update({
                'X-User-Id': bceid_guid,
                'Authorization': f'Bearer {self.access_token}',
                'X-Transaction-Id': transaction_id
            })
        else:
            headers.update({
                'X-User-Id': bceid_guid,
                'Authorization': f'Bearer {self.access_token}'
            })
        return headers
