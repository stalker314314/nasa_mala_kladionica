import os
import sys
from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'er7f9y^ruw3$0+*8_(h)2+(sx*vpdzr-zn==gs)i_vh7d+(hkm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
try:
    DEBUG = os.environ['NMK_DEBUG'] != '0'
except KeyError:
    pass

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'nmkapp.nmk_context_processor.player_stats'
            ],
        },
    },
]

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'nmkapp.apps.NmkappConfig',
    'anymail',
)

STATIC_URL = '/static/'

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'nmkapp.middlewares.TimezoneMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'nmk.urls'

WSGI_APPLICATION = 'nmk.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nmk',
        'HOST': 'localhost',
        'USER': 'postgres',
        'PASSWORD': ''
    }
}

# Covers regular testing and django-coverage
# if 'test' in sys.argv or 'test_coverage' in sys.argv:
#     DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

# Internationalization
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('sr', _('Serbian')),
    ('sr-Latn', _('Serbian latin')),
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

USE_I18N = True
USE_L10N = False

USE_TZ = True
TIME_ZONE = 'UTC'
TIMEZONE_SESSION_KEY = '_timezone'

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'
DATETIME_FORMAT = 'd.m.Y H:i'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'nmkapp', 'static')

SEND_MAIL = not DEBUG

ANYMAIL = {
    'MAILJET_API_KEY': '',
    'MAILJET_SECRET_KEY': '',
}
EMAIL_BACKEND = 'anymail.backends.mailjet.EmailBackend'

DEFAULT_FROM_EMAIL = "admin@sharkz.bet"
SERVER_EMAIL = 'admin@sharkz.bet'
ADMINS = [('Sharkz.bet', 'admin@sharkz.bet')]

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'nmk.worldcup2014@gmail.com'
EMAIL_HOST_PASSWORD = ''


LOGGING_DEBUG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'sb.log',
            'formatter': 'verbose',
            'when': 'midnight',
            'interval': 1
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}

LOGGING_PROD = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/sharkz.bet/sb.log',
            'formatter': 'verbose',
            'when': 'midnight',
            'interval': 1
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR'
        },
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'nmkapp': {
                'handlers': ['file'],
                'propagate': True,
                'level': 'DEBUG',
        },
        '': {
                'handlers': ['file'],
                'propogate': True,
                'level': 'INFO',
        }
    }
}


LOGGING = LOGGING_DEBUG

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

if DEBUG:
    INTERNAL_IPS = ('127.0.0.1',)

    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    INSTALLED_APPS += (
        'debug_toolbar',
    )

if not DEBUG:
    SECRET_KEY = os.environ['NMK_SECRET_KEY']
    DATABASES['default']['HOST'] = os.environ['NMK_DB_HOST']
    DATABASES['default']['NAME'] = os.environ['NMK_DB_NAME']
    DATABASES['default']['USER'] = os.environ['NMK_DB_USER']
    DATABASES['default']['PASSWORD'] = os.environ['NMK_DB_PASSWORD']
    ANYMAIL['MAILJET_API_KEY'] = os.environ['NMK_MAILJET_API_KEY']
    ANYMAIL['MAILJET_SECRET_KEY'] = os.environ['NMK_MAILJET_SECRET_KEY']
    ALLOWED_HOSTS = ['localhost', '.sharkz.bet', '.sharkz.bet.']
    LOGGING = LOGGING_PROD
    
    #enable loaders(caching) for prod
    del TEMPLATES['APP_DIRS']
    TEMPLATES['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader'
            ]
         )
    ]
