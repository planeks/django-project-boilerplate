from .base import *
from urllib.parse import urlparse
import logging
import os

DEBUG = config('DEBUG_MODE', default='NO') == 'YES'
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
INTERNAL_IPS = ['127.0.0.1']

CELERY_BROKER_URL = config('REDIS_URL')
CELERY_RESULT_BACKEND = config('REDIS_URL')

SENTRY_DSN = config('SENTRY_DSN')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )

    # INSTALLED_APPS += [
    #     'raven.contrib.django.raven_compat',
    # ]
    #
    # RAVEN_CONFIG = {
    #     'dsn': os.environ['SENTRY_DSN'],
    # }

    # MIDDLEWARE = (
    #     'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    # ) + MIDDLEWARE


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default='NO') == 'YES'

PARSED_REDIS_URL = urlparse(config('REDIS_URL'))
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
    }
}

# SESSION_ENGINE = 'django.contrib.sessions.backends.file'
# SESSION_FILE_PATH = config('SESSION_FILE_PATH', default=os.path.join(BASE_DIR, 'sessions'))

USE_HTTPS = config('USE_HTTPS', default='NO') == 'YES'

if USE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
