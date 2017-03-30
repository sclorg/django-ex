import uuid
from ipaddress import ip_address, ip_network

import sys
from django.conf import settings
from django.shortcuts import redirect


class BceidUser(object):
    def __init__(self, guid, first_name, last_name, user_type, is_authenticated):
        self.guid = guid
        self.first_name = first_name
        self.last_name = last_name
        self.type = user_type
        self.is_authenticated = is_authenticated


class BceidMiddleware(object):
    def process_request(self, request):

        localdev = settings.DEPLOYMENT_TYPE == 'localdev'

        # make sure the request didn't bypass the proxy
        if not localdev and not self.__request_came_from_proxy(request):
            print("Redirecting to " + settings.PROXY_BASE_URL + request.path, file=sys.stderr)
            return redirect(settings.PROXY_BASE_URL + request.path)

        if not localdev and request.META.get('HTTP_SM_USERDN', False):

            # 1. Real BCeID user / logged in
            request.bceid_user = BceidUser(
                guid=request.META.get('HTTP_SM_USERDN'),
                is_authenticated=True,
                user_type='BCEID',
                first_name=request.META.get('HTTP_SM_USER'),
                last_name=''
            )

        elif localdev and request.session.get('fake-bceid-guid', False):

            # 2. Fake BCeID user / logged in
            request.bceid_user = BceidUser(
                guid=request.session.get('fake-bceid-guid'),
                is_authenticated=True,
                user_type='FAKE',
                first_name=request.session.get('login-name',''),
                last_name=''
            )

        else:

            # 3.  Anonymous User / not logged in
            request.bceid_user = BceidUser(
                guid=None,
                is_authenticated=False,
                user_type='ANONYMOUS',
                first_name='',
                last_name=''
            )

    def process_response(self, request, response):
        return response


    def __request_came_from_proxy(self, request):
        """
        Validate that the request is coming from inside the BC Government data centre
        """
        # allow all OpenShift health checks
        if request.path == settings.FORCE_SCRIPT_NAME + 'health':
            return True

        # allow requests for static assets to bypass the proxy
        # (this is needed so WeasyPrint can request CSS)
        if request.path.startswith(settings.FORCE_SCRIPT_NAME[:-1] + settings.STATIC_URL):
            return True

        bcgov_network = ip_network(settings.BCGOV_NETWORK)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        forwarded_for = x_forwarded_for.split(',')

        if len(forwarded_for) == 0:
            return False

        for ip in forwarded_for:
            if ip !='' and ip_address(ip) in bcgov_network:
                return True
        return False