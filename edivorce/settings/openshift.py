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

WEASYPRINT_URL = 'http://weasyprint:5001'
WEASYPRINT_CSS_LOOPBACK = 'http://edivorce-django:8080'

# Django Compressor offline compression (triggered by setup.py during OpenShift build)
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# The app will be served out of a subdirectory of justice.gov.bc.ca
# PROD: /divorce
# TEST: /divorce-test
# DEV: /divorce-dev
#
# See nginx-proxy/conf.d/server.conf for related settings
#
DEPLOYMENT_TYPE = os.getenv('ENVIRONMENT_TYPE')

PROXY_URL_PREFIX = ''

if DEPLOYMENT_TYPE == 'dev':
    PROXY_URL_PREFIX = "/divorce-dev"
    DEBUG = True

if DEPLOYMENT_TYPE == 'test':
    PROXY_URL_PREFIX = "/divorce-test"


if DEPLOYMENT_TYPE == 'prod':
    PROXY_URL_PREFIX = "/divorce"


FORCE_SCRIPT_NAME = PROXY_URL_PREFIX + '/'
STATIC_URL = PROXY_URL_PREFIX + '/static/'
WEASYPRINT_CSS_LOOPBACK += PROXY_URL_PREFIX


