# ====================================
# IMPORTS E BASE
# ====================================
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


# ====================================
# CONFIGURAÇÕES BÁSICAS
# ====================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', cast=bool, default=False)
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

CSRF_TRUSTED_ORIGINS = [
    "https://notificai.lojabibelo.com.br",
]


# ====================================
# APLICATIVOS INSTALADOS
# ====================================
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do projeto
    'apps.accounts',
    'apps.workspaces',
    'apps.integrations',
]


# ====================================
# MIDDLEWARE
# ====================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom middleware
    'apps.workspaces.middleware.workspace.WorkspaceMiddleware',
]


# ====================================
# URL E TEMPLATES
# ====================================
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# ====================================
# BANCO DE DADOS
# ====================================
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', cast=int, default=0),
    }
}


# ====================================
# VALIDAÇÃO DE SENHAS
# ====================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ====================================
# INTERNACIONALIZAÇÃO
# ====================================
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ====================================
# STATIC E MEDIA FILES
# ====================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ====================================
# USUÁRIO PERSONALIZADO
# ====================================
AUTH_USER_MODEL = 'accounts.User'


# ====================================
# EMAIL
# ====================================
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.example.com')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='seu_email@example.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='sua_senha')


# ====================================
# LOGGING
# ====================================
import os

LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'file': {
            'level': config('LOG_LEVEL', default='INFO'),
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/app.log',
            'formatter': 'verbose',
        },
    },

    'loggers': {
        # Desativa log barulhento do Django
        'django': {
            'handlers': [],
            'level': 'WARNING',
            'propagate': False,
        },

        # Logger para seus apps (adicione outros se quiser)
        'accounts': {
            'handlers': ['file'],
            'level': config('LOG_LEVEL', default='DEBUG'),
            'propagate': False,
        },
                # Logger para seus apps (adicione outros se quiser)
        'integrations': {
            'handlers': ['file'],
            'level': config('LOG_LEVEL', default='DEBUG'),
            'propagate': False,
        },
    },
}

# ====================================
# CONFIGS CUSTOMIZADAS (Integrações, APIs etc.)
# ====================================
NUVEMSHOP_CLIENT_ID = config("CLIENT_ID")
NUVEMSHOP_CLIENT_SECRET = config("CLIENT_SECRET")
BASE_URL = config("WEBHOOK_URL")
