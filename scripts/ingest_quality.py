import os
import subprocess
import shutil

# Config - Universal mapping
STAGING = os.getenv("STAGING_PATH", "/data/staging")
MUSIC_DEST = os.getenv("MUSIC_DEST", "/data/music")
MOVIE_DEST = os.getenv("MOVIE_DEST", "/data/movies")
ACCEPTED_LOG = os.path.join(os.getenv("LOG_DIR", "."), "accepted.txt")
REJECTED_LOG = os.path.join(os.getenv("LOG_DIR", "."), "rejected.txt")
MIN_HEIGHT = int(os.getenv("MIN_HEIGHT", 480))

def get_media_info(file_path):
    try:
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=height:format=bit_rate", "-of", "csv=p=0", file_path]
        res = subprocess.run(cmd, capture_output=True, text=True).stdout.strip().split(',')
        height = int(res[0]) if res[0] else 0
        bitrate = int(res[1]) if len(res) > 1 and res[1] else 0
        return bitrate, height
    except:
        return 0, 0

def log_event(log_path, status, reason, file_path):
    with open(log_path, "a") as f:
        f.write(f"[{status}] {reason} | {file_path}\n")

def process_files():
    for f in [ACCEPTED_LOG, REJECTED_LOG]:
        if os.path.exists(f): os.remove(f)
    
    for root, _, files in os.walk(STAGING):
        for file in files:
            src = os.path.join(root, file)
            
            if file.lower().endswith(('.mp4', '.mkv', '.avi')):
                bitrate, height = get_media_info(src)
                dest = os.path.join(MOVIE_DEST, file)
                if height < MIN_HEIGHT:
                    log_event(REJECTED_LOG, "REJECT", f"Sub-DVD ({height}p)", src)
                elif os.path.exists(dest):
                    log_event(REJECTED_LOG, "REJECT", "Duplicate Movie", src)
                else:
                    log_event(ACCEPTED_LOG, "ACCEPT", f"Movie ({height}p)", src)
                    shutil.move(src, dest)
            
            elif file.lower().endswith(('.mp3', '.m4a', '.flac', '.wav')):
                bitrate, _ = get_media_info(src)
                dest = os.path.join(MUSIC_DEST, file)
                if os.path.exists(dest):
                    _, d_bitrate = get_media_info(dest)
                    if bitrate > d_bitrate:
                        log_event(ACCEPTED_LOG, "UPGRADE", f"{bitrate} > {d_bitrate}", src)
                        shutil.move(src, dest)
                    else:
                        log_event(REJECTED_LOG, "REJECT", f"Lower Bitrate ({bitrate} <= {d_bitrate})", src)
                else:
                    log_event(ACCEPTED_LOG, "NEW", f"Music ({bitrate} bps)", src)
                    shutil.move(src, dest)

if __name__ == "__main__":
    process_files()
