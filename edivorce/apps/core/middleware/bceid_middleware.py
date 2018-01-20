import datetime
from ipaddress import ip_address, ip_network

from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone

from ..models import BceidUser

login_delta = datetime.timedelta(hours=2)


class AnonymousUser():
    """
    Anonymous user, present mainly to provide authentication checks in templates
    """

    guid = None
    display_name = ''
    has_accepted_terms = False

    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True


anonymous_user = AnonymousUser()


class BceidMiddleware(object):  # pylint: disable=too-few-public-methods
    """
    Simple authentication middleware for operating in the BC Government
    OpenShift environment, with SiteMinder integration.

    For our purposes, SiteMinder is configured to add the following headers:

        SMGOV_USERGUID
        SMGOV_USERDISPLAYNAME
        SM_USER

    The first two are provided on pages configured to be protected by
    SiteMinder, which is currently just /login.  When a user goes to the login
    page, if the user is logged in, SiteMinder adds those headers with their
    BCeID values; if they're not logged in, it routes them through its
    login/signup page and then back to the login page, with those headers in
    place.  For unprotected pages, those headers are stripped if present,
    preventing spoofing.

    The third header is populated on every request that's proxied through
    SiteMinder.  For logged in users, it contains their ???; for anonymous
    users, it's empty.

    When we detect authentication by the presence of the first two headers, we
    store those values in the user's session. On all requests, we use them to
    access a local proxy object for the user (available as request.user).  For
    users that are not logged in, an Anonymous User substitute is present.

    In a local development environment, we generate a guid based on the login
    name and treat that guid/login name as guid/display name.
    """

    def process_request(self, request):  # pylint: disable=too-many-branches
        """
        Return None after populating request.user, or necessary redirects.

        If the request is not coming from inside the BC Government data centre,
        redirect the request through the proxy server.

        If the SiteMinder headers are present, indicating the user has just
        authenticated, save those headers to the session.

        Get the user's GUID and display name.  If they're present, and the user
        has authenticated (or we're in a local development environment), add
        the local proxy user to the request; if not, store the anonymous user
        instance.
        """

        # make sure the request didn't bypass the proxy
        if (settings.DEPLOYMENT_TYPE not in ['localdev', 'minishift'] and
                not self.__request_came_from_proxy(request)):
            return redirect(settings.PROXY_BASE_URL + request.path)

        # HTTP_SM_USER is available on both secure and unsecure pages.  If it
        # has a value then we know that the user is still logged into BCeID.
        # This is an additional check to make sure we aren't letting users
        # access the site via their session variables after logging out of bceid
        #
        # Note: It's still possible that a user has logged out of one BCeID and
        # logged into another BCeID via www.bceid.ca without clicking the logout
        # link on our app or closing the browser.  This is an extreme edge case,
        # and it's not pragmatic to code against it at this time.
        siteminder_user = request.META.get('HTTP_SM_USER', '')
        is_localdev = settings.DEPLOYMENT_TYPE in ['localdev', 'minishift']
        update_user = False

        guid = request.META.get('HTTP_SMGOV_USERGUID', '')
        displayname = request.META.get('HTTP_SMGOV_USERDISPLAYNAME', '')

        if guid:
            request.session['smgov_userguid'] = guid
        else:
            guid = request.session.get('smgov_userguid')

        if displayname:
            request.session['smgov_userdisplayname'] = displayname
        else:
            displayname = request.session.get('smgov_userdisplayname')

        if is_localdev:
            guid = request.session.get('fake_bceid_guid')
            displayname = request.session.get('login_name')

        if guid and (siteminder_user or is_localdev):
            request.user, created = BceidUser.objects.get_or_create(user_guid=guid)
            if created:
                request.session['first_login'] = True
            if siteminder_user:
                if created or not request.user.sm_user:
                    request.user.sm_user = siteminder_user
                    update_user = True
            if request.user.display_name != displayname:
                request.user.display_name = displayname
                update_user = True
            if (request.user.last_login is None or
                    timezone.now() - request.user.last_login > login_delta):
                request.user.last_login = timezone.now()
                update_user = True

            if update_user:
                request.user.save()
        else:
            request.user = anonymous_user

        return None

    def __request_came_from_proxy(self, request):
        """
        Return True if the request is coming from inside the BC Government data
        centre, False otherwise.

        Health checks and static resources are allowed from any source.  The
        latter is mainly so WeasyPrint can request CSS.
        """

        if request.path == settings.FORCE_SCRIPT_NAME + 'health':
            return True

        if request.path.startswith(settings.FORCE_SCRIPT_NAME[:-1] + settings.STATIC_URL):
            return True

        bcgov_network = ip_network(settings.BCGOV_NETWORK)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')
        forwarded_for = [ip.strip() for ip in x_forwarded_for if ip.strip() != '']

        return any([ip_address(ip) in bcgov_network for ip in forwarded_for])
