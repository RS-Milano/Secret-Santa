#!/bin/bash
set -e
PROJECT_DIR="/projects/Secret-Santa"
cd "$PROJECT_DIR" || exit
git fetch origin main
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)
if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
    git pull origin main
    docker-compose up -d --build
fi