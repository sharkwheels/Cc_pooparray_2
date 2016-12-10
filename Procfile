web: gunicorn app:app --log-file=-
worker: python bot.py
web: newrelic-admin run-program gunicorn -b "0.0.0.0:$PORT" -w 3 app:app