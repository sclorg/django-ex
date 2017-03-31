import uuid
from ipaddress import ip_address, ip_network

import sys
from django.conf import settings
from django.shortcuts import redirect


class BceidUser(object):
    def __init__(self, guid, display_name, user_type, is_authenticated):
        self.guid = guid
        self.display_name = display_name
        self.type = user_type
        self.is_authenticated = is_authenticated


class BceidMiddleware(object):
    def process_request(self, request):

        # Save SiteMinder headers to session variables.  /login* is the only actual
        # SiteMinder-protected part of the site, so the headers aren't availabale anywhere else
        if request.META.get('HTTP_SMGOV_USERGUID', ''):
            request.session['smgov_userguid'] = request.META.get('HTTP_SMGOV_USERGUID')

        if request.META.get('HTTP_SMGOV_USERDISPLAYNAME', ''):
            request.session['smgov_userdisplayname'] = request.META.get('HTTP_SMGOV_USERDISPLAYNAME')

        # get SiteMinder variables from the headers first, then from the session
        smgov_userguid = request.META.get('HTTP_SMGOV_USERGUID', request.session.get('smgov_userguid', False))
        smgov_userdisplayname = request.META.get('HTTP_SMGOV_USERDISPLAYNAME', request.session.get('smgov_userdisplayname', False))

        # HTTP_SM_USER is available on both secure and unsecure pages.  If it has a value then we know
        # that the user is still logged into BCeID
        # This is an additional check to make sure we aren't letting users access the site
        # via their session variables after logging out of bceid
        has_siteminder_auth = request.META.get('HTTP_SM_USER','') != ''

        # Note: It's still possible that a user has logged out of one BCeID and logged into another BCeID
        # via www.bceid.ca without clicking the logout link on our app or closing the browser.  This is an
        # extreme edge case, and it's not pragmatic to code against it at this time.

        # make sure the request didn't bypass the proxy
        if settings.DEPLOYMENT_TYPE != 'localdev' and not self.__request_came_from_proxy(request):
            print("Redirecting to " + settings.PROXY_BASE_URL + request.path, file=sys.stderr)
            return redirect(settings.PROXY_BASE_URL + request.path)

        if settings.DEPLOYMENT_TYPE != 'localdev' and has_siteminder_auth and smgov_userguid:

            # 1. Real BCeID user / logged in
            request.bceid_user = BceidUser(
                guid=smgov_userguid,
                is_authenticated=True,
                user_type='BCEID',
                display_name=smgov_userdisplayname
            )

        elif settings.DEPLOYMENT_TYPE == 'localdev' and request.session.get('fake_bceid_guid', False):

            # 2. Fake BCeID user / logged in
            request.bceid_user = BceidUser(
                guid=request.session.get('fake_bceid_guid'),
                is_authenticated=True,
                user_type='FAKE',
                display_name=request.session.get('login_name', '')
            )

        else:

            # 3.  Anonymous User / not logged in
            request.bceid_user = BceidUser(
                guid=None,
                is_authenticated=False,
                user_type='ANONYMOUS',
                display_name=''
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