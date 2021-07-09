#!/bin/bash

python3 manage.py collectstatic --no-input

if [[ -z "${WORKER_NUM}" ]]; then
  workers=3
else
  workers="${WORKER_NUM}"
fi

if [ "$DEBUG" == "False" ]
then
    gunicorn forge.wsgi:application --bind 0.0.0.0:8000 --workers $workers
else
    python3 manage.py runserver 0.0.0.0:8000
fi