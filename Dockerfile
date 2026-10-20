# One image for local development (docker compose) and for Railway.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TAILWIND_CLI_PATH=/home/app/.tailwind

RUN useradd --create-home --uid 1000 app
WORKDIR /app
RUN chown app:app /app

# DEV=1 (docker compose sets it) adds the test tools; Railway builds without it.
ARG DEV=0
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt \
 && if [ "$DEV" = "1" ]; then pip install -r requirements-dev.txt; fi

COPY --chown=app:app . .
USER app

# Build the CSS and collect static files into the image. Settings insist on a
# secret key when DEBUG is off; neither command uses it, so a placeholder is
# enough here. The real value comes from the environment at run time.
RUN SECRET_KEY=build-only python manage.py tailwind build \
 && SECRET_KEY=build-only python manage.py collectstatic --noinput

EXPOSE 8000
# Railway sets $PORT; locally it falls back to 8000.
CMD ["sh", "-c", "gunicorn config.wsgi --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --timeout 30 --access-logfile -"]
