#!/bin/bash

ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../.env"

if [ -f "$ENV_FILE" ]; then
    DATABASE_URL=$(grep DATABASE_URL "$ENV_FILE" | cut -d '=' -f2)
    DATABASE_PATH=$(echo "$DATABASE_URL" | sed 's|sqlite:////||' | tr -d '[:space:]')
else
    echo "Error: .env file not found at $ENV_FILE!" >&2
    exit 1
fi

if [ ! -f "$DATABASE_PATH" ]; then
    echo "Error: Database file not found at: $DATABASE_PATH" >&2
    exit 1
fi

BACKUP_DIR="$(dirname "$DATABASE_PATH")/backups"
BACKUP_DAYS=30

TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP_FILE="$BACKUP_DIR/$TIMESTAMP-$(basename "$DATABASE_PATH")"

mkdir -p "$BACKUP_DIR"

# SQLite backup
if sqlite3 "$DATABASE_PATH" ".backup '$BACKUP_FILE'"; then
    gzip "$BACKUP_FILE"
    echo "Backup created: $BACKUP_FILE.gz"
else
    echo "Backup failed!" >&2
    rm -f "$BACKUP_FILE"
fi

# Remove backups older than $BACKUP_DAYS
find "$BACKUP_DIR" -name "*-$(basename "$DATABASE_PATH").gz" -type f -mtime +$BACKUP_DAYS -delete 
