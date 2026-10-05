# Production image: waitress (WSGI) serving the Flask app.
# Config comes from environment variables (see docker-compose.yml / .env).
FROM python:3.13-slim

WORKDIR /srv/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Seed is idempotent (existing rows kept), so running it at every start is
# safe - it also creates the tables on first boot.
CMD ["sh", "-c", "python seed.py && waitress-serve --host 0.0.0.0 --port 8000 --threads 8 run:app"]
