FROM debian:bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV USE_UNIX_SOCKET 1
ENV USE_REDIS 1
ENV DJANGO_SETTINGS_MODULE medassistant.settings
ENV VIRTUAL_ENV=/MedAssistant02/medassistant-venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV SERVICE_USER=www-data
ENV SERVICE_GROUP=www-data

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-pip wget gnupg build-essential locales redis-server postgresql gunicorn python3-uvicorn \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen \
    && apt-get clean && rm -rf /var/lib/apt/lists/* && mkdir /var/www && \
    chown $SERVICE_USER:$SERVICE_GROUP /var/www && \
    chsh -s /bin/bash $SERVICE_USER


COPY ./requirements.txt /MedAssistant02/requirements.txt

RUN python3 -m pip install -r /MedAssistant02/requirements.txt --break-system-packages

COPY . /MedAssistant02

WORKDIR /MedAssistant02/medassistant

EXPOSE 8000
VOLUME /MedAssistant02/medassistant/app_medassistant/static/images
VOLUME /var/lib/postgresql

ENTRYPOINT ["/MedAssistant02/entrypoint.sh"]
