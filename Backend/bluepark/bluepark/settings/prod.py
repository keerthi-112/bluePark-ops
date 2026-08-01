"""
Production settings. No insecure defaults: every secret must come from
the environment, and the process fails fast at startup if one is missing
rather than silently running with a dev-grade fallback.
"""

from .base import *  # noqa: F401,F403
from .base import env

SECRET_KEY = env('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

DATABASES = {
    'default': env.db('DATABASE_URL'),
}

# Real-time kitchen updates (Phase 2) need a channel layer shared across
# worker processes -- InMemoryChannelLayer (dev default, see base.py)
# only works within a single process. channels_redis is the documented
# swap for production.
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [env('REDIS_URL')],
        },
    },
}

# WhiteNoise serves collectstatic's output directly from the app
# process -- no separate nginx/CDN container needed for this project's
# scale. Inserted right after SecurityMiddleware per WhiteNoise's own
# install instructions. Rebuilt explicitly (not mutating the imported
# base.MIDDLEWARE list in place) to keep the two settings modules'
# middleware stacks independently readable.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Security headers
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

# Deliberately NOT setting CSRF_COOKIE_HTTPONLY = True: every fetch()
# call across this app (cart, kitchen status updates, notifications,
# inventory stock adjustments, AI copilot, staff scheduling -- Phases
# 1-4) reads the csrftoken cookie directly via document.cookie to set
# the X-CSRFToken header, per Django's own documented pattern for
# JS-driven requests. Making that cookie HttpOnly would silently break
# every one of those endpoints in production while looking like a
# textbook security improvement -- exactly the kind of change this
# phase's "preserve all functionality" constraint rules out.
