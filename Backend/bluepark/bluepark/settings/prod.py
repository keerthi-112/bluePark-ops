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

DATABASES = {
    'default': env.db('DATABASE_URL'),
}

SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
