#!/bin/bash
set -e
PROJECT_DIR="/projects/Secret-Santa"
cd "$PROJECT_DIR" || exit

echo "Проверяем обновления в ветке main..."
git fetch origin main

LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
    echo "Обновления найдены. Пуллим и пересобираем контейнеры..."
    git pull origin main
    chmod +x deploy.sh
    docker compose up -d --build
    echo "Деплой завершён."
else
    echo "Обновлений нет. Деплой не требуется."
fi