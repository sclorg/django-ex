from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

DEBUG = True
CSRF_COOKIE_AGE = None
SESSION_COOKIE_AGE = 3600
TEMPLATES[0]["OPTIONS"]["debug"] = True

WEASYPRINT_URL = env('WEASYPRINT_URL', 'http://localhost:5005')
WEASYPRINT_IMAGE_LOOPBACK = 'http://host.docker.internal:8000'
WEASYPRINT_CSS_LOOPBACK = WEASYPRINT_IMAGE_LOOPBACK

DEPLOYMENT_TYPE = 'localdev'
REGISTER_BCEID_URL = '#'
REGISTER_BCSC_URL = '#'
PROXY_BASE_URL = ''
SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_ROOT = PROJECT_ROOT + '/edivorce/apps/core/static'
SASS_OUTPUT_STYLE = 'compressed'
CORS_ORIGIN_ALLOW_ALL = True

# CLAMAV settings
CLAMAV_ENABLED = env.bool('CLAMAV_ENABLED', True)
CLAMAV_PORT = env.int('CLAMAV_PORT', 3310)
CLAMAV_HOST = env('CLAMAV_HOST', 'localhost')

# Redis settings
REDIS_HOST = env('REDIS_HOST', 'localhost')
REDIS_PORT = env.int('REDIS_PORT', 6379)
REDIS_DB = env('REDIS_DB', '')
REDIS_PASSWORD = env('REDIS_PASSWORD', '')

# Keycloak OpenID Connect settings
# Provided by mozilla-django-oidc
EDIVORCE_KEYCLOAK_BASE_URL = env('EDIVORCE_KEYCLOAK_BASE_URL', 'http://localhost:8081')
EDIVORCE_KEYCLOAK_REALM = env('EDIVORCE_KEYCLOAK_REALM', 'justice')
KEYCLOAK_LOGOUT = f'{EDIVORCE_KEYCLOAK_BASE_URL}/auth/realms/{EDIVORCE_KEYCLOAK_REALM}/protocol/openid-connect/logout'
OIDC_OP_JWKS_ENDPOINT = f'{EDIVORCE_KEYCLOAK_BASE_URL}/auth/realms/{EDIVORCE_KEYCLOAK_REALM}/protocol/openid-connect/certs'
OIDC_OP_AUTHORIZATION_ENDPOINT = f'{EDIVORCE_KEYCLOAK_BASE_URL}/auth/realms/{EDIVORCE_KEYCLOAK_REALM}/protocol/openid-connect/auth'
OIDC_OP_TOKEN_ENDPOINT = f'{EDIVORCE_KEYCLOAK_BASE_URL}/auth/realms/{EDIVORCE_KEYCLOAK_REALM}/protocol/openid-connect/token'
OIDC_OP_USER_ENDPOINT = f'{EDIVORCE_KEYCLOAK_BASE_URL}/auth/realms/{EDIVORCE_KEYCLOAK_REALM}/protocol/openid-connect/userinfo'
OIDC_RP_CLIENT_ID = 'edivorce-app'
LOGIN_REDIRECT_URL = '/signin'

# eFiling Hub settings
EFILING_HUB_KEYCLOAK_BASE_URL = env('EFILING_HUB_KEYCLOAK_BASE_URL', '')
EFILING_HUB_KEYCLOAK_REALM = env('EFILING_HUB_KEYCLOAK_REALM', '')
EFILING_HUB_KEYCLOAK_CLIENT_ID = env('EFILING_HUB_KEYCLOAK_CLIENT_ID', '')
EFILING_HUB_API_BASE_URL = 'https://fla-nginx-proxy-qzaydf-dev.pathfinder.gov.bc.ca/api'
EFILING_HUB_ENABLED = env.bool('EFILING_HUB_ENABLED', False)
EFILING_BCEID = env('EFILING_BCEID', '', subcast=str)
