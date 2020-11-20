import json
from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TransactionTestCase
from django.test.client import RequestFactory

from edivorce.apps.core.utils.efiling_court_locations import EFilingCourtLocations

SAMPLE_COURTS_RESPONSE = {"courts": [{
    "id": 19227.0734,
    "identifierCode": "5871",
    "name": "100 Mile House Law Courts",
    "code": "OMH",
    "isSupremeCourt": False,
    "address": {
        "addressLine1": "160 Cedar Avenue South",
        "addressLine2": "Box 1060",
        "addressLine3": None,
        "postalCode": "V0K2E0",
        "cityName": "100 Mile House",
        "provinceName": "British Columbia",
        "countryName": "Canada"
    }
}]}


class EFilingCourtLocationsTests(TransactionTestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

        self.request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()

        self.locationsApi = EFilingCourtLocations()

    def _mock_response(self, text=""):
        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.text = text
        return mock_resp

    @mock.patch('edivorce.apps.core.utils.efiling_court_locations.EFilingCourtLocations._get_api')
    def test_locations_success(self, mock_get_api):
        self.request.session['bcgov_userguid'] = '70fc9ce1-0cd6-4170-b842-bbabb88452a9'
        mock_get_api.return_value = self._mock_response(
            text=json.dumps(SAMPLE_COURTS_RESPONSE))
        locations = self.locationsApi.courts(self.request)

        self.assertEqual(locations["100 Mile House"]["location_id"], "5871")
        self.assertEqual(locations["100 Mile House"]["postal"], "V0K2E0")
        self.assertEqual(locations["100 Mile House"]["address_1"], "160 Cedar Avenue South")
        self.assertEqual(locations["100 Mile House"]["address_2"], "Box 1060")
        self.assertIsNone(locations["100 Mile House"]["address_3"])
