#!/bin/sh

set -e

. /venv/bin/activate
flask --app mtgdeckstats init-db
exec gunicorn --bind 0.0.0.0:${PORT:-8080} --forwarded-allow-ips='*' wsgi:app