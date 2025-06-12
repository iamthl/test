#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python backend_pre_start.py

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8000 