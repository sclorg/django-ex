from rest_framework import authentication


class BCeIDAuthentication(authentication.BaseAuthentication):
    """
    Make the DRF user the BCeID user populated in our middleware, to avoid DRF
    overwriting our user for API calls.

    This relies on our middleware entirely for authentication.
    """

    def authenticate(self, request):
        try:
            request.user = request._user  # pylint: disable=protected-access
        except:
            request.user = request._request.user  # pylint: disable=protected-access
        return (request.user, None)
