import os
import subprocess
import json
from pathlib import Path

# Environment-aware paths
target_dir = Path(os.getenv("MUSIC_DEST", "/mnt/primary/@data/Music"))
source_dir = target_dir / "Music"

def get_quality_score(path):
    cmd = [
        "ffprobe", "-v", "error", 
        "-show_entries", "stream=width,height,bit_rate", 
        "-of", "json", str(path)
    ]
    try:
        data = json.loads(subprocess.check_output(cmd).decode())
        streams = data.get("streams", [])
        
        # Check Video Resolution
        video = next((s for s in streams if s.get("width")), None)
        if video:
            return int(video["width"]) * int(video["height"])
            
        # Check Audio Bitrate
        audio = next((s for s in streams if s.get("bit_rate")), None)
        if audio:
            return int(audio["bit_rate"])
            
        return 0
    except Exception:
        return 0

def run_sync():
    if not source_dir.exists():
        return

    for root, _, files in os.walk(source_dir):
        for name in files:
            source_file = Path(root) / name
            rel_path = source_file.relative_to(source_dir)
            target_file = target_dir / rel_path
            
            target_file.parent.mkdir(parents=True, exist_ok=True)

            if not target_file.exists():
                source_file.rename(target_file)
                continue

            if get_quality_score(source_file) > get_quality_score(target_file):
                source_file.rename(target_file)

if __name__ == "__main__":
    run_sync()
