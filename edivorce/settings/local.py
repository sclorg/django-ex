from .base import *
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE'),
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
    }
}

WEASYPRINT_URL = 'http://localhost:5005'
WEASYPRINT_CSS_LOOPBACK = 'http://10.200.10.1:8000'
