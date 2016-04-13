nohup celery -A verifier_app.tasks worker --loglevel=INFO --concurrency=24 > celery.out && nohup python manage.py server > manage.out
