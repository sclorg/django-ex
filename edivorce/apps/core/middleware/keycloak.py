from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from mozilla_django_oidc.utils import absolutify


class EDivorceKeycloakBackend(OIDCAuthenticationBackend):

    def verify_claims(self, claims):
        verified = super(EDivorceKeycloakBackend, self).verify_claims(claims)
        print(claims)

        return verified

    def create_user(self, claims):
        user = super(EDivorceKeycloakBackend, self).create_user(claims)

        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.display_name = "{} {}".format(user.first_name, user.last_name).strip()
        user.sm_user = claims.get('preferred_username', '')
        user.user_guid = claims.get('universal-id', '')
        user.save()

        self.request.session['bcgov_userguid'] = user.user_guid

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.display_name = "{} {}".format(user.first_name, user.last_name).strip()
        user.sm_user = claims.get('preferred_username', '')
        user.user_guid = claims.get('universal-id', '')
        user.save()

        self.request.session['bcgov_userguid'] = user.user_guid

        return user

    def filter_users_by_claims(self, claims):
        user_guid = claims.get('universal-id')
        if not user_guid:
            return self.UserModel.objects.none()
        return self.UserModel.objects.filter(user_guid=user_guid)


def keycloak_logout(request):
    request.session.flush()

    redirect_uri = absolutify(request, settings.FORCE_SCRIPT_NAME)

    return f'{settings.KEYCLOAK_LOGOUT}?redirect_uri={redirect_uri}'
