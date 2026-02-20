FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir \
    flask \
    Flask-SQLAlchemy \
    Flask-Migrate \
    SQLAlchemy \
    PyMySQL \
    redis \
    openpyxl \
    gunicorn \
    pycryptodome \
    pytest
EXPOSE 8000
CMD ["sh", "start.sh"]
