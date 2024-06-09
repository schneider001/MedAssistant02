FROM debian:bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV USE_UNIX_SOCKET 1
ENV USE_REDIS 1
ENV DJANGO_SETTINGS_MODULE medassistant.settings
ENV SERVICE_USER=www-data
ENV SERVICE_GROUP=www-data

ARG PORT=8000
ENV PORT=$PORT
ARG NGINX_PORT=80
ENV NGINX_PORT=$NGINX_PORT

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-pip wget gnupg build-essential locales redis-server postgresql gunicorn python3-uvicorn nginx \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen \
    && apt-get clean && rm -rf /var/lib/apt/lists/* && mkdir -p /var/www && \
    chown $SERVICE_USER:$SERVICE_GROUP /var/www && \
    chsh -s /bin/bash $SERVICE_USER

COPY ./requirements.txt /MedAssistant02/requirements.txt

RUN python3 -m pip install -r /MedAssistant02/requirements.txt --break-system-packages

RUN echo "\
server {\
    listen ${NGINX_PORT};\
    server_name 127.0.0.1 localhost; \
    access_log /var/log/nginx/access.log; \
    error_log /var/log/nginx/error.log; \
    location /media {\
        autoindex on;\
        alias /var/www/;\
    }\
    location / {\
        proxy_pass http://localhost:${PORT};\
        proxy_set_header Host \$host;\
        proxy_set_header X-Real-IP \$remote_addr;\
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\
        proxy_set_header X-Forwarded-Proto \$scheme;\
    }\
}" > /etc/nginx/conf.d/default.conf && sed -i "s/user www-data;/user ${SERVICE_USER};/" /etc/nginx/nginx.conf

COPY . /MedAssistant02

WORKDIR /MedAssistant02/medassistant

EXPOSE $PORT
VOLUME /var/www/
VOLUME /var/lib/postgresql

ENTRYPOINT ["/MedAssistant02/entrypoint.sh"]
