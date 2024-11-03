#!/bin/bash
python -m alembic upgrade head
exec uvicorn main:app --workers 4
#exec gunicorn -k main.Worker -w 4 -b 0.0.0.0:8000 --preload \
#    -c gunicorn_hooks_config.py main:app
#
