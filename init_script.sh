#!/bin/bash

echo "Init script started"

# Check if the models folder exists indicating database has been initialized
if [ ! -d "/app/migrations/models" ]; then
    echo "Running aerich init-db"
    aerich init-db
else
    echo "Skipping aerich init-db"
fi

# Run migrations
aerich upgrade

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload