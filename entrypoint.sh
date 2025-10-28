#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run database migrations
alembic upgrade head

# Execute the command passed as arguments to this script
exec "$@"