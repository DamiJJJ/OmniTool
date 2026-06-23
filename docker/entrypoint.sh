#!/bin/sh
set -e

echo "[entrypoint] Start OmniTool. Uruchamiam migracje bazy (flask db upgrade)..."

# MariaDB w stacku może podnosić się dłużej niż aplikacja przy pierwszym starcie.
# Ponawiamy `flask db upgrade` aż baza odpowie (lub do limitu prób).
ATTEMPTS=0
MAX_ATTEMPTS=40
until flask db upgrade; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
    echo "[entrypoint] BŁĄD: migracje nie powiodły się po ${MAX_ATTEMPTS} próbach. Sprawdź DATABASE_URL i kontener bazy."
    exit 1
  fi
  echo "[entrypoint] Baza jeszcze niegotowa (próba ${ATTEMPTS}/${MAX_ATTEMPTS}). Czekam 3s..."
  sleep 3
done

echo "[entrypoint] Migracje OK. Startuję gunicorn na 0.0.0.0:8000..."
exec gunicorn \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --access-logfile - \
  --error-logfile - \
  app:app
