#!/bin/bash
# Get absolute path to the current directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CRON_CMD="0 11 * * * $PROJECT_DIR/run_auto.sh >> $PROJECT_DIR/claim.log 2>&1"

# Remove existing job for this script (to allow updating)
(crontab -l 2>/dev/null | grep -v "$PROJECT_DIR/run_auto.sh") | crontab -

# Add the new job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
echo "Cron job updated successfully."
