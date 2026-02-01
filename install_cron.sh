#!/bin/bash
# Get absolute path to the current directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CRON_CMD="0 11 * * * $PROJECT_DIR/run_auto.sh >> $PROJECT_DIR/claim.log 2>&1"

# Check if the job already exists
(crontab -l 2>/dev/null | grep -F "$PROJECT_DIR/run_auto.sh") && echo "Cron job already exists." && exit 0

# Add the job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
echo "Cron job added successfully."
