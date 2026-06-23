FROM python:3.12-slim

# Ustawienia środowiska Pythona/Flaska
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

WORKDIR /app

# Zależności najpierw (lepszy cache warstw)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kod aplikacji (wraz z katalogiem migrations/ - potrzebny do `flask db upgrade`)
COPY . .

# Entrypoint: poczekaj na bazę -> migracje -> gunicorn
RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
