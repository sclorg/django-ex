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
SESSION_COOKIE_AGE = None
TEMPLATES[0]["OPTIONS"]["debug"] = True

WEASYPRINT_URL = 'http://localhost:5005'
WEASYPRINT_CSS_LOOPBACK = 'http://10.200.10.1:8000'

DEPLOYMENT_TYPE = 'localdev'
REGISTER_URL = '#'
PROXY_BASE_URL = ''
SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_ROOT = PROJECT_ROOT + '/edivorce/apps/core/static'
SASS_OUTPUT_STYLE = 'compressed'
