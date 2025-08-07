#!/bin/sh
set -e

# Default to port 8080 if the PORT environment variable is not set.
UVICORN_PORT=${PORT:-8080}

# Run the uvicorn server, replacing the shell process with the new process
exec uvicorn main:app --host 0.0.0.0 --port "$UVICORN_PORT"
