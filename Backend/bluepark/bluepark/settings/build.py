"""
Settings used only for `collectstatic` at Docker build time.

Running collectstatic under settings.dev avoided needing real secrets
at build time, but dev.py doesn't set STORAGES, so it uses Django's
plain static storage -- no manifest file gets built. settings.prod
then loads WhiteNoise's CompressedManifestStaticFilesStorage at
runtime, which requires that manifest to resolve every {% static %}
tag, so every page raised "Missing staticfiles manifest entry".

This module uses prod's exact static storage backend (so what's built
here is what prod actually serves) while keeping dev's safe,
no-real-secrets-required fallbacks for everything else --
collectstatic never touches the database or needs a real SECRET_KEY.
"""

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env

SECRET_KEY = env('SECRET_KEY', default='django-insecure-build-only-do-not-use-in-production')

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
}

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
