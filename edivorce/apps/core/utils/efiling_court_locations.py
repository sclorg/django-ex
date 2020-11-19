import json
import logging
import requests
import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

from .efiling_hub_caller_base import EFilingHubCallerBase

logger = logging.getLogger(__name__)


class EFilingCourtLocations(EFilingHubCallerBase):

    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        EFilingHubCallerBase.__init__(self)

    def _get_api(self, request, url, bceid_guid, headers={}):
        # make sure we have an access token
        if not self.access_token:
            if not self._get_token(request):
                raise Exception('EFH - Unable to get API Token')

        headers = self._set_headers(headers, bceid_guid, self.access_token)
        response = requests.get(url, headers=headers)
        logging.debug(f'EFH - Get Locations {response.status_code} {response.text}')

        if response.status_code == 401:
            # not authorized .. try refreshing token
            if self._refresh_token(request):
                headers = self._set_headers(headers, bceid_guid, self.access_token)
                response = requests.get(url, headers=headers)
                logging.debug(f'EFH - Get Locations Retry {response.status_code} {response.text}')

        return response

    def courts(self, request):

        if cache.get('courts'):
            return cache.get('courts')

        bceid_guid = self._get_bceid(request)

        # if bceid_guid is None .. we basically have an anonymous user so raise an error
        if bceid_guid is None:
            raise PermissionDenied()

        url = f'{self.api_base_url}/courts?courtLevel=S'
        print('DEBUG: ' + url)

        response = self._get_api(request, url, bceid_guid, headers={})

        if response.status_code == 200:
            cso_locations = json.loads(response.text)
            locations = {}

            for location in cso_locations['courts']:
                city = location['address']['cityName']
                locations[city] = {
                    'address_1': location['address']['addressLine1'],
                    'address_2': location['address']['addressLine2'],
                    'address_3': location['address']['addressLine3'],
                    'postal': location['address']['postalCode'],
                    'location_id': location['identifierCode']
                }

            cache.set('courts', locations)

            return locations

        if response.status_code == 401:
            print(response.headers.get('WWW-Authenticate', ''))
            return {"Error calling court locations API": {"status_code": "401", "text": "authentication failed"}}

        return {"Error calling court locations API": {"status_code": str(response.status_code), "text": response.text}}
