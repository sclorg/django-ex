import json
from unittest import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.test import TransactionTestCase
from django.test.client import RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile

from edivorce.apps.core.utils.efiling_submission import EFilingSubmission
from edivorce.apps.core.utils.efiling_packaging import EFilingPackaging, PACKAGE_PARTY_FORMAT, PACKAGE_DOCUMENT_FORMAT

SAMPLE_TOKEN_RESPONSE = {
    "access_token": "klkadlfjadsfkj",
    "expires_in": 300,
    "refresh_expires_in": 1800,
    "refresh_token": "ljasdfjaofijwekfjadslkjf",
    "token_type": "bearer",
    "not-before-policy": 0,
    "session_state": "bed88a31-4d73-4f31-a4ee-dd8aa225d801",
    "scope": "email profile"
}

INITIAL_DOC_UPLOAD_RESPONSE = {
    "submissionId": "70fc9ce1-0cd6-4170-b842-bbabb88452a9",
    "received": 1
}

GENERATE_URL_RESPONSE = {
    "expiryDate": 1597775531035,
    "efilingUrl": "http://efiling.gov.bc.ca/efiling?submissionId=adfadsf&transactionId=adsfadsf"
}

GENERATE_URL_RESPONSE_ERROR = {
    "error": "403",
    "message": "Request does not meet criteria"
}


class EFilingSubmissionTests(TransactionTestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

        self.request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()
        
        self.hub = EFilingSubmission(initial_filing=True)
        self.packaging = EFilingPackaging(initial_filing=True)

    def _mock_response(self, status=200, text="Text", json_data=None, raise_for_status=None):
        mock_resp = mock.Mock()
        mock_resp.raise_for_status = mock.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        mock_resp.status_code = status
        mock_resp.text = text
        if json_data:
            mock_resp.json = mock.Mock(
                return_value=json_data
            )
        return mock_resp

    @mock.patch('requests.post')
    def test_get_token(self, mock_request_post):
        mock_request_post.return_value = self._mock_response(
            text=json.dumps(SAMPLE_TOKEN_RESPONSE))

        self.assertTrue(self.hub._get_token(self.request))
        self.assertEqual(self.request.session['access_token'],
                         SAMPLE_TOKEN_RESPONSE['access_token'])

    @mock.patch('requests.post')
    def test_get_token_error(self, mock_request_post):
        mock_request_post.return_value = self._mock_response(
            text=json.dumps(SAMPLE_TOKEN_RESPONSE), status=401)

        self.assertFalse(self.hub._get_token(self.request))
        self.assertFalse("access_token" in self.request.session)

    @mock.patch('requests.post')
    def test_renew_token(self, mock_request_post):
        mock_request_post.return_value = self._mock_response(
            text=json.dumps(SAMPLE_TOKEN_RESPONSE))
        self.request.session['refresh_token'] = 'alskdfjadlfads'

        self.assertTrue(self.hub._refresh_token(self.request))
        self.assertEqual(self.request.session['access_token'],
                         SAMPLE_TOKEN_RESPONSE['access_token'])

    @mock.patch('requests.post')
    def test_renew_token_anon(self, mock_request_post):
        # if we don't have a refresh token in session, this should fail
        mock_request_post.return_value = self._mock_response(
            text=json.dumps(SAMPLE_TOKEN_RESPONSE))

        self.assertFalse(self.hub._refresh_token(self.request))
        self.assertFalse("access_token" in self.request.session)

    @mock.patch('requests.post')
    def test_renew_token_error(self, mock_request_post):
        mock_request_post.return_value = self._mock_response(
            text=json.dumps(SAMPLE_TOKEN_RESPONSE), status=401)
        self.request.session['refresh_token'] = 'alskdfjadlfads'

        self.assertTrue(self.hub._refresh_token(self.request))
        self.assertEqual(self.request.session['access_token'],
                         SAMPLE_TOKEN_RESPONSE['access_token'])

    @mock.patch('requests.post')
    def test_get_api_success(self, mock_request_post):
        mock_request_post.return_value = self._mock_response(
            text=json.dumps(INITIAL_DOC_UPLOAD_RESPONSE))
        self.request.session['access_token'] = 'aslkfjadskfjd'

        response = self.hub._get_api(
            self.request, 'https://somewhere.com', 'alksdjfa', 'kasdkfd', {})

        self.assertTrue(response)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.text)
        self.assertTrue("submissionId" in response)

    @mock.patch('requests.post')
    def test_get_api_expired_token(self, mock_request_post):
        self.request.session['access_token'] = 'aslkfjadskfjd'
        self.request.session['refresh_token'] = 'alskdfjadlfads'

        # we want 3 mock side effects for post .. a 401 on the first and success on token renewal
        mock_request_post.side_effect = [
            self._mock_response(text=json.dumps(INITIAL_DOC_UPLOAD_RESPONSE), status=401),
            self._mock_response(text=json.dumps(SAMPLE_TOKEN_RESPONSE)),
            self._mock_response(text=json.dumps(INITIAL_DOC_UPLOAD_RESPONSE))
        ]

        response = self.hub._get_api(
            self.request, 'https://somewhere.com', 'alksdjfa', 'kasdkfd', {})

        self.assertTrue(response)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.text)
        self.assertTrue("submissionId" in response)

    @mock.patch('requests.post')
    def test_get_api_no_token(self, mock_request_post):
        mock_request_post.return_value = self._mock_response(
            text=json.dumps(INITIAL_DOC_UPLOAD_RESPONSE))

        with self.assertRaises(Exception):
            response = self.hub._get_api(
                self.request, 'https://somewhere.com', 'alksdjfa', 'kasdkfd', {})

    def test_transaction_id_current(self):
        self.request.session['transaction_id'] = 'alksdjflaskdjf'
        guid = self.hub._get_transaction(self.request)

        self.assertEqual(guid, 'alksdjflaskdjf')

    def test_transaction_id_empty(self):
        self.assertFalse('transaction_id' in self.request.session)
        guild = self.hub._get_transaction(self.request)

        self.assertTrue('transaction_id' in self.request.session)

    def test_bceid_get_current(self):
        self.request.session['bcgov_userguid'] = '70fc9ce1-0cd6-4170-b842-bbabb88452a9'
        with self.settings(DEPLOYMENT_TYPE='prod'):
            bceid = self.hub._get_bceid(self.request)
            self.assertEqual(bceid, '70fc9ce1-0cd6-4170-b842-bbabb88452a9')

    def test_bceid_anonymous_user(self):
        with self.settings(DEPLOYMENT_TYPE='prod'):
            bceid = self.hub._get_bceid(self.request)
            self.assertFalse(bceid)

    @mock.patch('edivorce.apps.core.utils.efiling_submission.EFilingSubmission._get_api')
    def test_upload_success(self, mock_get_api):
        self.request.session['bcgov_userguid'] = '70fc9ce1-0cd6-4170-b842-bbabb88452a9'
        with self.settings(DEPLOYMENT_TYPE='prod'):
            mock_get_api.side_effect = [
                self._mock_response(text=json.dumps(INITIAL_DOC_UPLOAD_RESPONSE)),
                self._mock_response(text=json.dumps(GENERATE_URL_RESPONSE))
            ]
            redirect, msg = self.hub.upload(self.request, {})

            self.assertTrue(redirect)
            self.assertEqual(redirect, GENERATE_URL_RESPONSE['efilingUrl'])
            self.assertEqual(msg, 'success')

    @mock.patch('edivorce.apps.core.utils.efiling_submission.EFilingSubmission._get_api')
    def test_upload_failed_initial_upload(self, mock_get_api):
        self.request.session['bcgov_userguid'] = '70fc9ce1-0cd6-4170-b842-bbabb88452a9'
        with self.settings(DEPLOYMENT_TYPE='prod'):
            mock_get_api.side_effect = [
                self._mock_response(text=json.dumps(INITIAL_DOC_UPLOAD_RESPONSE), status=401),
                self._mock_response(text=json.dumps(GENERATE_URL_RESPONSE))
            ]
            redirect, msg = self.hub.upload(self.request, {})

            self.assertFalse(redirect)

    @mock.patch('edivorce.apps.core.utils.efiling_submission.EFilingSubmission._get_api')
    def test_upload_failed_generate_url(self, mock_get_api):
        self.request.session['bcgov_userguid'] = '70fc9ce1-0cd6-4170-b842-bbabb88452a9'
        with self.settings(DEPLOYMENT_TYPE='prod'):
            mock_get_api.side_effect = [
                self._mock_response(text=json.dumps(INITIAL_DOC_UPLOAD_RESPONSE)),
                self._mock_response(text=json.dumps(GENERATE_URL_RESPONSE_ERROR), status=403)
            ]
            redirect, msg = self.hub.upload(self.request, {})

            self.assertFalse(redirect)
