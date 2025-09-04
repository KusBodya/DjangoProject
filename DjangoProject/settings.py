import os
from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность и режимы
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret')
DEBUG = os.getenv('DJANGO_DEBUG', '0') == '1'
# Можно перечислять через запятую в .env: DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
ALLOWED_HOSTS = [h for h in os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h]

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',              # админка полезна для наполнения БД
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',                   # DRF
    'app',                              # заменить на имя вашего приложения
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DjangoProject.urls'

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

WSGI_APPLICATION = 'DjangoProject.wsgi.application'
ASGI_APPLICATION = 'DjangoProject.asgi.application'

# База данных
# По умолчанию SQLite, для Docker-профиля задайте переменные:
# SQL_ENGINE=django.db.backends.postgresql, SQL_HOST=db, SQL_* и т.п.
SQL_ENGINE = os.getenv('SQL_ENGINE', 'django.db.backends.sqlite3')
if SQL_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': SQL_ENGINE,
            'NAME': os.getenv('SQL_DATABASE', str(BASE_DIR / 'db.sqlite3')),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': SQL_ENGINE,                          # django.db.backends.postgresql
            'NAME': os.getenv('SQL_DATABASE', 'quotes'),
            'USER': os.getenv('SQL_USER', 'quotes_user'),
            'PASSWORD': os.getenv('SQL_PASSWORD', 'quotes_pass'),
            'HOST': os.getenv('SQL_HOST', 'db'),
            'PORT': os.getenv('SQL_PORT', '5432'),
            'CONN_MAX_AGE': int(os.getenv('SQL_CONN_MAX_AGE', '60')),  # держать соединение
        }
    }

# DRF (минимальные настройки)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # для разработки; в продакшене ужесточить
    ],
}

# Пароли
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Локализация
LANGUAGE_CODE = os.getenv('DJANGO_LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.getenv('DJANGO_TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True

# Статика/медиа
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'    # для collectstatic в продакшене
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Первичный ключ по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Логирование (удобно в Docker)
LOGLEVEL = os.getenv('DJANGO_LOGLEVEL', 'info')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': LOGLEVEL.upper(),
    },
}
