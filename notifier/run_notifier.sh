#!/bin/bash
# Epic Games Free Game Notifier Runner
# Runs daily to check for new free games and send email notifications

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment variables from .env file
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | grep -v '^$' | xargs)
fi

echo "[$(date)] Starting Epic Games Free Game Notifier..."

# Run the notification script
cd "$SCRIPT_DIR"
if python3 notify_free_games.py; then
    echo "[$(date)] Notifier finished successfully."
    exit 0
else
    EXIT_CODE=$?
    echo "[$(date)] Notifier failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi
