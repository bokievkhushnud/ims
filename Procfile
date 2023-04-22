web: gunicorn ims.wsgi --log-file -
worker: celery -A ims worker --loglevel=info
celery_beat: celery -A ims beat --loglevel=info
