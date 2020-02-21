import os
import dj_database_url
from django.utils.crypto import get_random_string
from decouple import config, Csv


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_NAME = config('PROJECT_NAME')

SECRET_KEY = config("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',

    # 'mptt',
    # 'easy_thumbnails',
    # 'django_select2',
    # 'rest_framework',
    # 'rest_framework.authtoken',

    'apps.core',
    'apps.accounts',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = '%s.urls' % PROJECT_NAME

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, PROJECT_NAME, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

WSGI_APPLICATION = '%s.wsgi.application' % PROJECT_NAME


# Database
DATABASES = {
    'default': dj_database_url.config(default=config('DATABASE_URL')),
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
LANGUAGE_CODE = config('LANGUAGE_CODE', default='en')

LANGUAGES = [
    ('en', 'English'),
]

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(BASE_DIR, 'staticfiles'))

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, PROJECT_NAME, 'static'),
)

MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'


AUTH_USER_MODEL = 'accounts.User'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

LOCALE_PATHS = [
    # os.path.join(BASE_DIR, PROJECT_NAME, 'locale'),
]

SESSION_COOKIE_DOMAIN = config('SESSION_COOKIE_DOMAIN', default=None)
CSRF_COOKIE_SAMESITE = None
SESSION_COOKIE_SAMESITE = None

# THUMBNAIL_BASEDIR = 'thumbs'
# THUMBNAIL_ALIASES = {
#     '': {
#         'avatar': {
#             'size': (200, 200),
#             'background': '#cccccc',
#         },
#     },
# }

# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.SessionAuthentication',
#         'rest_framework.authentication.TokenAuthentication',
#     ]
# }

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@tabbli.com')
EMAIL_BCC_ADDRESSES = config('EMAIL_BCC_ADDRESSES', default='', cast=Csv())

PROJECT_CONFIGURATION = config('DJANGO_SETTINGS_MODULE', default='').split('.')[-1]
USE_HTTPS = False

# Google integration
GOOGLE_TAG_MANAGER = os.environ.get('GOOGLE_TAG_MANAGER', '')

# ELASTICSEARCH_URLS = config('ELASTICSEARCH_URLS', default='http://localhost:9200', cast=Csv())
# ELASTICSEARCH_INDICES_PREFIX = config('ELASTICSEARCH_INDICES_PREFIX', default=PROJECT_NAME)

SITE_URL = config('SITE_URL', default='')
