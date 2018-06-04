from .base import *

def openshift_db_config():
    '''
    Database config based on the django-ex openshift sample application
    '''
    service_name = os.getenv('DATABASE_SERVICE_NAME', '').upper()

    engines = {
        'sqlite': 'django.db.backends.sqlite3',
        'postgresql': 'django.db.backends.postgresql_psycopg2',
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
DEPLOYMENT_TYPE = os.getenv('ENVIRONMENT_TYPE')

PROXY_URL_PREFIX = ''
PROXY_BASE_URL = os.getenv('PROXY_BASE_URL', 'https://justice.gov.bc.ca')

if DEPLOYMENT_TYPE == 'dev':
    PROXY_URL_PREFIX = os.getenv('PROXY_URL_PREFIX', '/divorce-dev')
    DEBUG = True
    REGISTER_URL = 'https://www.test.bceid.ca/directories/bluepages/details.aspx?serviceID=5522'

if DEPLOYMENT_TYPE == 'test':
    PROXY_URL_PREFIX = os.getenv('PROXY_URL_PREFIX', '/divorce-test')
    REGISTER_URL = 'https://www.test.bceid.ca/directories/bluepages/details.aspx?serviceID=5521'

if DEPLOYMENT_TYPE == 'prod':
    PROXY_URL_PREFIX = os.getenv('PROXY_URL_PREFIX', '/divorce')
    REGISTER_URL = 'https://www.bceid.ca/directories/bluepages/details.aspx?serviceID=5203'
    # Google Tag Manager (Production)
    GTM_ID = 'GTM-W4Z2SPS'

if DEPLOYMENT_TYPE == 'minishift':
    DEBUG = True
    REGISTER_URL = '#'
    PROXY_BASE_URL = ''

# Internal Relative Urls
FORCE_SCRIPT_NAME = PROXY_URL_PREFIX + '/'
STATIC_URL = PROXY_URL_PREFIX + '/static/'

# Internal Urls (within the OpenShift project)
WEASYPRINT_URL = 'http://weasyprint:5001'
WEASYPRINT_CSS_LOOPBACK = 'http://edivorce-django:8080'
WEASYPRINT_CSS_LOOPBACK += PROXY_URL_PREFIX

# External URLs
LOGOUT_URL_TEMPLATE = 'https://logon.gov.bc.ca/clp-cgi/logoff.cgi?returl=%s%s&retnow=1'
LOGOUT_URL = LOGOUT_URL_TEMPLATE % (PROXY_BASE_URL, PROXY_URL_PREFIX)

# Basic authentication settings (meant for dev/test environments)
BASICAUTH_ENABLED = os.getenv('BASICAUTH_ENABLED', '').lower() == 'true'
BASICAUTH_USERNAME = os.getenv('BASICAUTH_USERNAME', '')
BASICAUTH_PASSWORD = os.getenv('BASICAUTH_PASSWORD', '')

# Lock down the session cookie settings
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

if DEPLOYMENT_TYPE != 'minishift':
    SESSION_COOKIE_PATH = PROXY_URL_PREFIX
    SESSION_COOKIE_SECURE=True
