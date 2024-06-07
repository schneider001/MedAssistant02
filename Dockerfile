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

RUN apt-get update && apt-get install -y python3 python3-pip wget gnupg build-essential locales redis-server postgresql python3-venv \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv $VIRTUAL_ENV

COPY ./requirements.txt /MedAssistant02/requirements.txt

RUN . $VIRTUAL_ENV/bin/activate && \
    pip install --upgrade pip && \
    pip install -r /MedAssistant02/requirements.txt

COPY . /MedAssistant02

WORKDIR /MedAssistant02/medassistant

EXPOSE 8000
VOLUME /MedAssistant02/medassistant/app_medassistant/static/images
VOLUME /var/lib/postgresql

ENTRYPOINT ["/MedAssistant02/entrypoint.sh"]
