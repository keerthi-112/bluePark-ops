# BluePark production image. Runs via Daphne (not `runserver`) so
# WebSocket support (Phase 2's real-time kitchen queue) works the same
# in production as it does with `manage.py runserver` locally.

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# libjpeg/zlib: Pillow (menu item image uploads, Phase 1) needs these
# at runtime even when installed from a wheel.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# collectstatic needs *a* settings module to import, but doesn't touch
# the database -- using settings.dev here (which has safe zero-config
# fallbacks for SECRET_KEY/DATABASE_URL) avoids requiring real
# production secrets to be present at build time, when they normally
# aren't (those come from the environment at *run* time via
# docker-compose / the hosting platform).
RUN DJANGO_SETTINGS_MODULE=bluepark.settings.dev python manage.py collectstatic --noinput

ENV DJANGO_SETTINGS_MODULE=bluepark.settings.prod

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "bluepark.asgi:application"]
