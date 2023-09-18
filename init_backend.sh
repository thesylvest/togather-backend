#!/bin/bash

echo "Init script started"
aerich init -t app.main.tortoise_config

if [ ! -d "/app/migrations/models" ]; then
    aerich init-db
    echo "Running aerich init-db"
else
    echo "Skipping aerich init-db"
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
