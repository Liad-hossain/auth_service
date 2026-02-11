#!/bin/bash
set -e

echo "🔄 Running database migrations..."
make get-migrate-linux
make migrations-up

echo "🚀 Starting application..."
exec python src/main.py
