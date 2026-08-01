"""
Local development settings. Zero-config by default: falls back to a
SQLite database and an insecure-but-fine dev secret key if no `.env`
is present, so `runserver` works right after `pip install -r requirements.txt`.
"""

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env

SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-only-do-not-use-in-production')

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
}
