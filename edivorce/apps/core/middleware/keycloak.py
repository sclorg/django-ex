from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class EDivorceKeycloakBackend(OIDCAuthenticationBackend):

    def verify_claims(self, claims):
        verified = super(EDivorceKeycloakBackend, self).verify_claims(claims)
        print(claims)

        return verified
