#!/bin/bash
cd "$(dirname "$0")/claimer"

# Check if node_modules exists, if not install
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    npx playwright install firefox
fi

echo "Starting Epic Games Claimer..."
echo "NOTE: If this is your first run, a browser window will open."
echo "Please log in to your Epic Games account in that window."
echo "Once logged in, the script will proceed to claim games."
echo "-------------------------------------------------------"

# Run with SHOW=1 to ensure the browser is visible for login
SHOW=1 /opt/homebrew/bin/node epic-games.js
