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

WEASYPRINT_URL = 'http://localhost:5005'
WEASYPRINT_CSS_LOOPBACK = 'http://10.200.10.1:8000'

DEPLOYMENT_TYPE = 'localdev'
REGISTER_URL = '#'
REGISTER_SC_URL ='#'
PROXY_BASE_URL = ''
SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_ROOT = PROJECT_ROOT + '/edivorce/apps/core/static'
SASS_OUTPUT_STYLE = 'compressed'

LOGOUT_URL = '/accounts/logout/'

# CLAMAV settings
CLAMAV_ENABLED = env.bool('CLAMAV_ENABLED', True)
CLAMAV_TCP_PORT = env.int('CLAMAV_TCP_PORT', 3310)
CLAMAV_TCP_ADDR = env('CLAMAV_TCP_ADDR', 'localhost')

# Redis settings
REDIS_HOST = env('REDIS_HOST', 'localhost')
REDIS_PORT = env.int('REDIS_PORT', 6379)
REDIS_DB = env('REDIS_DB', '')
REDIS_PASSWORD = env('REDIS_PASSWORD', '')
