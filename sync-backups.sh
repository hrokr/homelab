#!/bin/sh
# Path: ./sync-backups.sh (Run inside Alpine container)

set -e # If there is an error, just exit

SOURCE="/mnt/primary"
DEST="/mnt/failover"
INTERNAL_CONFIG="/config"
STATE_FILE="/config/.failover_sync_state"

if mountpoint -q "$DEST"; then
    echo "Failover detected. Executing sync."
    
    # 1. Sync all media folders (Music, Videos, etc.)
    # The --one-file-system flag prevents rsync from trying to back up the backup drive into itself
    rsync -avhW --no-compress --delete --one-file-system "$SOURCE/" "$DEST/"
    
    # 2. Sync app configs to a dedicated backup subfolder
    mkdir -p "$DEST/Backups/Configs"
    rsync -avh --delete "$INTERNAL_CONFIG/" "$DEST/Backups/Configs/"
    
    # 3. Record success
    date +%s > "$STATE_FILE"
    echo "Sync successful: $(date)"
else
    if [ -f "$STATE_FILE" ]; then
        LAST_SYNC=$(cat "$STATE_FILE")
        NOW=$(date +%s)
        DAYS_SINCE=$(( (NOW - LAST_SYNC) / 86400 ))

        if [ "$DAYS_SINCE" -ge 10 ]; then
            # Inside Alpine, wall may not reach your host terminal.
            # This will appear in 'docker logs backup_manager'
            echo "ALERT: Failover missing for $DAYS_SINCE days."
        fi
    fi
    echo "Failover drive not found. Skipping."
fi
