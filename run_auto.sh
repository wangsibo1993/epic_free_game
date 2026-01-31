#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CLAIMER_DIR="$SCRIPT_DIR/claimer"

# Go to the claimer directory
cd "$CLAIMER_DIR"

echo "[$(date)] Starting auto-claim process..."

# Run in headless mode (default when SHOW is not set)
# We use the full path to node to ensure cron works
if /opt/homebrew/bin/node epic-games.js; then
    echo "[$(date)] Auto-claim finished successfully."
    # Run success alert script
    echo "[$(date)] Sending success notification..."
    cd "$SCRIPT_DIR"
    /opt/homebrew/bin/node alert_mailer.js success
else
    EXIT_CODE=$?
    echo "[$(date)] Auto-claim failed with exit code $EXIT_CODE."
    
    # Run failure alert script
    echo "[$(date)] Sending failure alert..."
    cd "$SCRIPT_DIR"
    /opt/homebrew/bin/node alert_mailer.js failure
fi
