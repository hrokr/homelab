import subprocess
import os
import time
import sys

# Dynamic path resolution
PRIMARY = os.getenv("PRIMARY_MOUNT", "/mnt/primary")
FAILOVER = os.getenv("FAILOVER_MOUNT", "/mnt/failover")
STATE_FILE = os.getenv("STATE_FILE", "/config/.failover_sync_state")

def get_more_data_in():
    """Prepend check: Validate mount and stale state."""
    if not os.path.ismount(FAILOVER):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                last_sync = int(f.read().strip())
            
            days_since = (int(time.time()) - last_sync) // 86400
            if days_since >= 10:
                print(f"ALERT: Failover missing for {days_since} days.")
        return False
    return True

def run_btrfs_sync():
    print("Getting more data in: Initializing Btrfs block-level sync.")
    try:
        snap_id = f"snap_{int(time.time())}"
        subprocess.run(f"btrfs subvolume snapshot -r {PRIMARY} {PRIMARY}/.snaps/{snap_id}", shell=True, check=True)
        
        # Incremental Send/Receive
        subprocess.run(f"btrfs send {PRIMARY}/.snaps/{snap_id} | btrfs receive {FAILOVER}/", shell=True, check=True)
        
        with open(STATE_FILE, "w") as f:
            f.write(str(int(time.time())))
            
    except subprocess.CalledProcessError as e:
        print(f"Btrfs sync failed: {e}")

if __name__ == "__main__":
    if get_more_data_in():
        run_btrfs_sync()
