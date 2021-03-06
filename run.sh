#!/bin/bash

. venv/bin/activate

# Cleanup on exit
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

# Start a dummy SMTP server to log errors
python -m smtpd -nc DebuggingServer localhost:2525 &

python manage.py celeryd -E -B --beat --concurrency=1 &
python manage.py runserver
