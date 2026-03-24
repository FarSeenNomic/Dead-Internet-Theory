#!/bin/bash

set -e

while true; do
    echo "----- $(date) -----"
    echo "Updating repository..."
    git pull || echo "Git pull failed"

    echo "Starting Flask..."
    flask run || echo "Flask exited"

    echo "Restarting in 3 seconds..."
    sleep 3
done