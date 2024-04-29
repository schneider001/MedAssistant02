#!/bin/bash
set -e

stop_postgres() {
    echo "Stopping PostgreSQL service..."
    service postgresql stop
    exit 0
}

trap stop_postgres SIGTERM

chown -R postgres:postgres /var/lib/postgresql/data
chown -R postgres:postgres /MedAssistant02/medassistant/app_medassistant/static/images

service postgresql start
service redis-server start

# Check if the database exists
if su - postgres -c "psql -lqt | cut -d \| -f 1 | grep -qw medassistant"; then
    # database exists
    echo "Database already exists, skipping initialization."
else
    # database does not exist
    # create and initialize the database
    su -m postgres -c 'createdb -E '\''UTF8'\'' -l '\''en_US.UTF-8'\'' -T template0 -O postgres medassistant'
    su -m postgres -c 'python /MedAssistant02/medassistant/manage.py makemigrations && python /MedAssistant02/medassistant/manage.py migrate && python /MedAssistant02/medassistant/populate_db.py'
fi

su -m postgres -c 'gunicorn medassistant.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 3'



