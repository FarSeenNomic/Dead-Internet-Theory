#!/bin/bash
#
set -e

while true; do
    echo "----- $(date) -----"
    echo "Updating repository..."
    git pull || echo "Git pull failed"

    echo "Starting Flask..."
    python3 -m flask --app app:wib run --host 0.0.0.0 || echo "Flask exited"

    echo "Restarting in 3 seconds..."
    sleep 3
done