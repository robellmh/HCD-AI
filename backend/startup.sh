# #!/bin/bash
# python -m alembic upgrade head
# exec gunicorn -k main.Worker -w 4 -b 0.0.0.0:8000 --preload \
#     -c gunicorn_hooks_config.py main:app
# #
python -m alembic upgrade head

# Start Uvicorn server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --reload --timeout-keep-alive 60
#exec gunicorn -k main.Worker -w 4 -b 0.0.0.0:8000 --preload \
#    -c gunicorn_hooks_config.py main:app
