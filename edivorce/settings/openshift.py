from mozilla_django_oidc import utils
from .base import *


def openshift_db_config():
    '''
    Database config based on the django-ex openshift sample application
    '''
    service_name = os.getenv('DATABASE_SERVICE_NAME', '').upper()

    engines = {
        'sqlite': 'django.db.backends.sqlite3',
        'postgresql': 'django.db.backends.postgresql',
        'mysql': 'django.db.backends.mysql',
    }

    if service_name:
        engine = engines.get(os.getenv('DATABASE_ENGINE'), engines['sqlite'])
    else:
        engine = engines['sqlite']
    name = os.getenv('DATABASE_NAME')
    if not name and engine == engines['sqlite']:
        name = os.path.join(PROJECT_ROOT, 'db.sqlite3')

    return {
        'ENGINE': engine,
        'NAME': name,
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('{}_SERVICE_HOST'.format(service_name)),
        'PORT': os.getenv('{}_SERVICE_PORT'.format(service_name)),
    }


DATABASES = {
    'default': openshift_db_config()
}

# Django Compressor offline compression (triggered by wsgi.py during OpenShift deployment)
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# The app will be served out of a subdirectory of justice.gov.bc.ca via reverse-proxy
# PROD: /divorce
# TEST: /divorce-test
# DEV: /divorce-dev
#
# See nginx-proxy/conf.d/server.conf for related settings
#
DEPLOYMENT_TYPE = env('ENVIRONMENT_TYPE', 'unittest')

PROXY_URL_PREFIX = ''
PROXY_BASE_URL = os.getenv('PROXY_BASE_URL', 'https://justice.gov.bc.ca')

if DEPLOYMENT_TYPE in ['dev', 'unittest']:
    DEBUG = True
    # Keycloak OpenID Connect settings
    OIDC_OP_JWKS_ENDPOINT = 'https://sso-dev.pathfinder.gov.bc.ca/auth/realms/tz0e228w/protocol/openid-connect/certs'
    OIDC_OP_AUTHORIZATION_ENDPOINT = 'https://sso-dev.pathfinder.gov.bc.ca/auth/realms/tz0e228w/protocol/openid-connect/auth'
    OIDC_OP_TOKEN_ENDPOINT = 'https://sso-dev.pathfinder.gov.bc.ca/auth/realms/tz0e228w/protocol/openid-connect/token'
    OIDC_OP_USER_ENDPOINT = 'https://sso-dev.pathfinder.gov.bc.ca/auth/realms/tz0e228w/protocol/openid-connect/userinfo'
    KEYCLOAK_LOGOUT = 'https://sso-dev.pathfinder.gov.bc.ca/auth/realms/tz0e228w/protocol/openid-connect/logout'
    OIDC_RP_CLIENT_ID = 'e-divorce-app'

if DEPLOYMENT_TYPE == 'dev':
    PROXY_URL_PREFIX = os.getenv('PROXY_URL_PREFIX', '/divorce')
    CSRF_COOKIE_AGE = None
    SESSION_COOKIE_AGE = 3600
    REGISTER_BCEID_URL = 'https://www.test.bceid.ca/directories/bluepages/details.aspx?serviceID=5522'
    REGISTER_BCSC_URL = 'https://logontest7.gov.bc.ca/clp-cgi/fed/fedLaunch.cgi?partner=fed38&partnerList=fed38&flags=0001:0,7&TARGET=http://dev.justice.gov.bc.ca/divorce/oidc/authenticate'

if DEPLOYMENT_TYPE == 'test':
    PROXY_URL_PREFIX = os.getenv('PROXY_URL_PREFIX', '/divorce')
    REGISTER_BCEID_URL = 'https://www.test.bceid.ca/directories/bluepages/details.aspx?serviceID=5521'
    REGISTER_BCSC_URL = 'https://logontest7.gov.bc.ca/clp-cgi/fed/fedLaunch.cgi?partner=fed38&partnerList=fed38&flags=0001:0,7&TARGET=http://test.justice.gov.bc.ca/divorce/oidc/authenticate'
    # Keycloak OpenID Connect settings
    OIDC_OP_JWKS_ENDPOINT = 'https://sso-test.pathfinder.gov.bc.ca/auth/realms/XXXXXXXX/protocol/openid-connect/certs'
    OIDC_OP_AUTHORIZATION_ENDPOINT = 'https://sso-test.pathfinder.gov.bc.ca/auth/realms/XXXXXXXX/protocol/openid-connect/auth'
    OIDC_OP_TOKEN_ENDPOINT = 'https://sso-test.pathfinder.gov.bc.ca/auth/realms/XXXXXXXX/protocol/openid-connect/token'
    OIDC_OP_USER_ENDPOINT = 'https://sso-test.pathfinder.gov.bc.ca/auth/realms/XXXXXXXX/protocol/openid-connect/userinfo'
    KEYCLOAK_LOGOUT = 'https://sso-test.pathfinder.gov.bc.ca/auth/realms/XXXXXXXX/protocol/openid-connect/logout'
    OIDC_RP_CLIENT_ID = 'XXXXXXXX'

if DEPLOYMENT_TYPE == 'prod':
    PROXY_URL_PREFIX = os.getenv('PROXY_URL_PREFIX', '/divorce')
    REGISTER_BCEID_URL = 'https://www.bceid.ca/directories/bluepages/details.aspx?serviceID=5203'
    REGISTER_BCSC_URL = 'https://logon7.gov.bc.ca/clp-cgi/fed/fedLaunch.cgi?partner=fed49&partnerList=fed49&flags=0001:0,8&TARGET=http://justice.gov.bc.ca/divorce/oidc/authenticate'
    # Keycloak OpenID Connect settings
    OIDC_OP_JWKS_ENDPOINT = 'https://sso.pathfinder.gov.bc.ca/auth/realms/XXXXXXXX/protocol/openid-connect/certs'
    OIDC_OP_AUTHORIZATION_ENDPOINT = 'https://sso.pathfinder.gov.bc.ca/auth/realms/XXXXXXXX/protocol/openid-connect/auth'
    OIDC_OP_TOKEN_ENDPOINT = 'https://sso.pathfinder.gov.bc.ca/auth/realms/XXXXXXXX/protocol/openid-connect/token'
    OIDC_OP_USER_ENDPOINT = 'https://sso.pathfinder.gov.bc.ca/auth/realms/XXXXXXXX/protocol/openid-connect/userinfo'
    KEYCLOAK_LOGOUT = 'https://sso.pathfinder.gov.bc.ca/auth/realms/XXXXXXXX/protocol/openid-connect/logout'
    OIDC_RP_CLIENT_ID = 'XXXXXXXX'
    # Google Tag Manager (Production)
    GTM_ID = 'GTM-W4Z2SPS'

if DEPLOYMENT_TYPE == 'minishift':
    DEBUG = True
    REGISTER_BCEID_URL = '#'
    REGISTER_BCSC_URL = '#'
    PROXY_BASE_URL = ''
    # Keycloak OpenID Connect settings
    OIDC_OP_JWKS_ENDPOINT = 'http://localhost:8081/auth/realms/justice/protocol/openid-connect/certs'
    OIDC_OP_AUTHORIZATION_ENDPOINT = 'http://localhost:8081/auth/realms/justice/protocol/openid-connect/auth'
    OIDC_OP_TOKEN_ENDPOINT = 'http://localhost:8081/auth/realms/justice/protocol/openid-connect/token'
    OIDC_OP_USER_ENDPOINT = 'http://localhost:8081/auth/realms/justice/protocol/openid-connect/userinfo'
    KEYCLOAK_LOGOUT = 'http://localhost:8081/auth/realms/justice/protocol/openid-connect/logout'
    OIDC_RP_CLIENT_ID = 'edivorce-app'

# Internal Relative Urls
FORCE_SCRIPT_NAME = PROXY_URL_PREFIX + '/'
STATIC_URL = PROXY_URL_PREFIX + '/static/'

# Internal Urls (within the OpenShift project)
WEASYPRINT_URL = 'http://weasyprint:5001'
WEASYPRINT_IMAGE_LOOPBACK = 'http://edivorce-django:8080'
WEASYPRINT_CSS_LOOPBACK = WEASYPRINT_IMAGE_LOOPBACK + PROXY_URL_PREFIX

# Basic authentication settings (meant for dev/test environments)
BASICAUTH_ENABLED = os.getenv('BASICAUTH_ENABLED', '').lower() == 'true'
BASICAUTH_USERNAME = os.getenv('BASICAUTH_USERNAME', '')
BASICAUTH_PASSWORD = os.getenv('BASICAUTH_PASSWORD', '')

# Lock down the session cookie settings
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

if DEPLOYMENT_TYPE != 'minishift':
    SESSION_COOKIE_PATH = PROXY_URL_PREFIX
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# CLAMAV settings
CLAMAV_ENABLED = True
CLAMAV_TCP_PORT = 3310
CLAMAV_TCP_ADDR = os.getenv('CLAMAV_TCP_ADDR', 'clamav')

# Redis settings
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = 6379
REDIS_DB = ''
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# Keycloak OpenID Connect settings
LOGIN_REDIRECT_URL = PROXY_URL_PREFIX + '/signin'

# Enable Efiling Hub
EFILING_HUB_ENABLED = True

def monkey_absolutify(request, path):
    return PROXY_BASE_URL + path


# monkey-patching mozilla_django_oidc.utils.absolutify so it doesn't
# return urls prefixed with 'http://edivorce-django:8080' on OpenShift
utils.absolutify = monkey_absolutify
