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
TEMPLATES[0]["OPTIONS"]["debug"] = True

WEASYPRINT_URL = 'http://localhost:5005'
WEASYPRINT_CSS_LOOPBACK = 'http://10.200.10.1:8000'
