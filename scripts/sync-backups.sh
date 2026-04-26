#!/bin/sh
# Path: ./sync-backups.sh

SOURCE="/mnt/primary"
DEST="/mnt/failover"
STATE_FILE="/config/.failover_sync_state"

if mountpoint -q "$DEST"; then
    # Perform rsync
    rsync -avhW --no-compress --delete "$SOURCE/Music/" "$DEST/Music/"
    rsync -avhW --no-compress --delete "$SOURCE/Videos/" "$DEST/Videos/"
    
    date +%s > "$STATE_FILE"
else
    if [ -f "$STATE_FILE" ]; then
        LAST_SYNC=$(cat "$STATE_FILE")
        NOW=$(date +%s)
        DAYS_SINCE=$(( (NOW - LAST_SYNC) / 86400 ))

        if [ "$DAYS_SINCE" -ge 10 ]; then
            # Replace with preferred notification method
            echo "ALERT: Failover missing for $DAYS_SINCE days."
        fi
    fi
fi
