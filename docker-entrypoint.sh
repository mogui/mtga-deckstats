#!/bin/sh

set -e

. /venv/bin/activate
exec gunicorn --bind 0.0.0.0:${PORT:-8080} --forwarded-allow-ips='*' mtgdeckstats:app