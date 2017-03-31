import base64

import sys
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string


class BasicAuthMiddleware(object):
    """
    Simple Basic Authentication module to password protect test environments
    based on : https://djangosnippets.org/snippets/2468/
    This could have also been implemented via the NGINX-PROXY, but a Django
    implementation allows environment variables to be used to store
    username + password
    """
    def process_request(self, request):

        # allow all OpenShift health checks
        if request.path == settings.FORCE_SCRIPT_NAME + 'health':
            return None

        # allow ajax requests -
        # basic auth through ajax is tricky, and besides, this isn't really
        # intended as security.  It's just to prevent users from
        # logging into the wrong environment.
        if request.path.startswith(settings.FORCE_SCRIPT_NAME + 'api/'):
            return None

        # allow all static files
        if request.path.startswith(settings.FORCE_SCRIPT_NAME[:-1] + settings.FORCE_SCRIPT_NAME + 'static/'):
            return None

        # check if the middleware is enabled in settings
        if not settings.BASICAUTH_ENABLED:
            return None

        if not 'HTTP_AUTHORIZATION' in request.META:
            return self.__not_authorized()
        else:
            authentication = request.META['HTTP_AUTHORIZATION']
            (authmeth, auth) = authentication.split(' ', 1)
            if 'basic' != authmeth.lower():
                return self.__not_authorized()
            auth = base64.b64decode(auth.strip()).decode('utf-8')
            username, password = auth.split(':', 1)
            if username == settings.BASICAUTH_USERNAME and password == settings.BASICAUTH_PASSWORD:
                return None

            return self.__not_authorized()

    def __not_authorized(self):
        auth_template = render_to_string('401.html')
        response = HttpResponse(auth_template, content_type="text/html")
        response['WWW-Authenticate'] = 'Basic realm="Development"'
        response.status_code = 401
        return response
