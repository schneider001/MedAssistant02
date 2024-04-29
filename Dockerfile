FROM python:3.10-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV USE_UNIX_SOCKET 1
ENV USE_REDIS 1
ENV DJANGO_SETTINGS_MODULE medassistant.settings


RUN apt-get update && apt-get install -y wget gnupg build-essential locales redis-server \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update && apt-get install -y postgresql-13 \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN echo "local all postgres peer" >> /etc/postgresql/13/main/pg_hba.conf

COPY . /MedAssistant02

WORKDIR /MedAssistant02/medassistant

RUN pip install --upgrade pip && \
    pip install -r ../requirements.txt gunicorn uvicorn[standard] redis #move to requirements?

EXPOSE 8000
VOLUME /MedAssistant02/medassistant/app_medassistant/static/images
VOLUME /var/lib/postgresql/data

ENTRYPOINT ["/MedAssistant02/entrypoint.sh"]
