#!/bin/bash
# Sync project to Raspberry Pi
PI_USER="pi"
PI_HOST="raspberrypi.local"
PI_DEST="/home/pi/ff-led-scoreboard"

rsync -avz --exclude 'venv/' --exclude '__pycache__/' --exclude '*.pyc' \
  ./ ${PI_USER}@${PI_HOST}:${PI_DEST}

echo "Deploy complete → ${PI_USER}@${PI_HOST}:${PI_DEST}"
