#!/bin/bash
# Install cron job for Epic Games Free Game Notifier
# Runs daily at 11:00 AM

# Get absolute path to the notifier directory
NOTIFIER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$NOTIFIER_DIR")"

# Define cron job (11:00 AM daily)
CRON_CMD="0 11 * * * $NOTIFIER_DIR/run_notifier.sh >> $PROJECT_DIR/notifier.log 2>&1"

# Remove existing notifier cron job (to allow updating)
(crontab -l 2>/dev/null | grep -v "$NOTIFIER_DIR/run_notifier.sh") | crontab -

# Add the new job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "========================================================================"
echo "✅ Notifier cron job installed successfully!"
echo "========================================================================"
echo ""
echo "Schedule: Every day at 11:00 AM"
echo "Script: $NOTIFIER_DIR/run_notifier.sh"
echo "Log: $PROJECT_DIR/notifier.log"
echo ""
echo "To view current cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove this cron job:"
echo "  crontab -l | grep -v 'run_notifier.sh' | crontab -"
echo ""
echo "========================================================================"
