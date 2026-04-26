import os
import shutil

# Dynamic path resolution
base_dir = os.getenv("MUSIC_DEST", "/mnt/primary/Music")
source_parent = os.path.join(base_dir, "sift")

def normalize(name):
    return "".join(e for e in name if e.isalnum()).lower()

def merge():
    if not os.path.exists(source_parent):
        return

    # 1. Map existing standard folders
    standard_folders = {}
    for d in os.listdir(base_dir):
        full_path = os.path.join(base_dir, d)
        if os.path.isdir(full_path) and d != "sift" and not d.startswith('.'):
            standard_folders[normalize(d)] = full_path

    # 2. Process the sift folder
    for artist_folder in os.listdir(source_parent):
        src_path = os.path.join(source_parent, artist_folder)
        if not os.path.isdir(src_path):
            continue
            
        target_dir = standard_folders.get(normalize(artist_folder))

        if not target_dir:
            target_dir = os.path.join(base_dir, artist_folder)
            os.makedirs(target_dir, exist_ok=True)

        for root, _, files in os.walk(src_path):
            for file in files:
                s_file = os.path.join(root, file)
                rel_path = os.path.relpath(s_file, src_path)
                d_file = os.path.join(target_dir, rel_path)
                
                os.makedirs(os.path.dirname(d_file), exist_ok=True)

                if os.path.exists(d_file):
                    if os.path.getsize(s_file) == os.path.getsize(d_file):
                        os.remove(s_file)
                    else:
                        shutil.move(s_file, d_file)
                else:
                    shutil.move(s_file, d_file)

if __name__ == "__main__":
    merge()
