import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'er7f9y^ruw3$0+*8_(h)2+(sx*vpdzr-zn==gs)i_vh7d+(hkm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'nmkapp.nmk_context_processor.player_stats'
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader'
                    ]
                )
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
    'nmkapp',
    "djrill"
)

STATIC_URL = '/static/'

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'HOST': 'kokanovic.postgres.database.azure.com',
        'USER': 'nmk@kokanovic',
        'PASSWORD': 'nmk!'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Belgrade'

USE_I18N = True

USE_L10N = False

USE_TZ = False

LOGIN_URL='/login/'
LOGOUT_URL='/logout/'
LOGIN_REDIRECT_URL='/'
DATETIME_FORMAT = 'd.m.Y H:i'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'nmkapp', 'static')

SEND_MAIL=False
MANDRILL_API_KEY = ""
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

DEFAULT_FROM_EMAIL = "nmk@kokanovic.org"
SERVER_EMAIL='nmk@kokanovic.org'
ADMINS = [('Branko Kokanovic', 'nmk@kokanovic.org')]

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
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'nmk.log',
            'formatter': 'verbose',
            'when': 'midnight',
            'interval': 1
        },
        'console' : {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers':['file', 'console'],
            'propagate': True,
            'level':'INFO',
        },
    }
}

LOGGING_PROD = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/nmk/nmk.log',
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
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
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
    ALLOWED_HOSTS = ['localhost', '.nmk.kokanovic.org', '.nmk.kokanovic.org.']
    SEND_MAIL = True
    LOGGING = LOGGING_PROD