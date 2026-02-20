#!/bin/sh
set -eu

python - <<'PY'
import os, time
import pymysql

host = os.getenv("MYSQL_HOST", "mysql")
port = int(os.getenv("MYSQL_PORT", "3306"))
user = os.getenv("MYSQL_USER", "hackshop_user")
password = os.getenv("MYSQL_PASSWORD", "hackshop_password")
db = os.getenv("MYSQL_DB", "hackshop_db")

for _ in range(90):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=db, connect_timeout=2)
        conn.close()
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("MySQL not ready")
PY


if [ -d "migrations" ]; then
  flask --app app db upgrade
else
  python - <<'PY'
from app import app
from app.models.db import db

with app.app_context():
    db.create_all()
PY
fi

python scripts/ensure_indexes.py || true

WEB_WORKERS="${WEB_WORKERS:-4}"
WEB_THREADS="${WEB_THREADS:-4}"
WEB_TIMEOUT="${WEB_TIMEOUT:-120}"

exec gunicorn -w "${WEB_WORKERS}" -k gthread --threads "${WEB_THREADS}" -t "${WEB_TIMEOUT}" -b 0.0.0.0:8000 app:app
