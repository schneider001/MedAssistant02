#!/bin/bash
set -e

stop_postgres() {
    echo "Stopping PostgreSQL service..."
    service postgresql stop
    exit 0
}

trap stop_postgres SIGTERM

echo "Starting PostgreSQL service..."
service postgresql start
echo "PostgreSQL service started."

# Ensure the wwwdata user exists in PostgreSQL
if ! su - postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='$SERVICE_USER'\"" | grep -q 1; then
    echo "Creating PostgreSQL user..."
    su - postgres -c "createuser -s $SERVICE_USER"
    echo "PostgreSQL user created."
	echo "local   all             $SERVICE_USER                                peer" >> /etc/postgresql/*/main/pg_hba.conf
fi

chown $SERVICE_USER:$SERVICE_GROUP /var/lib/postgresql

service redis-server start
echo "Redis service started."

nginx -t
chown -R $SERVICE_USER:$SERVICE_GROUP /var/www/ && chmod -R 0755 /var/www/
service nginx start
echo "Nginx service started."

chown -R $SERVICE_USER:$SERVICE_GROUP /MedAssistant02

# Check if the database exists
if su - $SERVICE_USER -c "psql -lqt | cut -d \| -f 1 | grep -qw medassistant"; then
    # database exists
    echo "Database already exists, skipping initialization."
	su -m $SERVICE_USER -c "python3 /MedAssistant02/medassistant/manage.py makemigrations && python3 /MedAssistant02/medassistant/manage.py migrate"
else
    # database does not exist
    # create and initialize the database
    echo "Creating and initializing the database..."
    su -m $SERVICE_USER -c "createdb -E 'UTF8' -l 'en_US.UTF-8' -T template0 -O $SERVICE_USER medassistant"
    su -m $SERVICE_USER -c "python3 /MedAssistant02/medassistant/manage.py makemigrations && python3 /MedAssistant02/medassistant/manage.py migrate && python3 /MedAssistant02/medassistant/populate_db.py"
    echo "Database created and initialized."
fi

su -m $SERVICE_USER -c "python3 /MedAssistant02/medassistant/manage.py collectstatic --noinput"
su -m $SERVICE_USER -c "gunicorn medassistant.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT --workers 3"

