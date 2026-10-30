import glob
import os
import shutil

dst_root = "/kaggle/working/results"
count = 0
for path in glob.glob("/kaggle/input/**/*.json", recursive=True):
    parts = path.split("/")
    if "data" in parts or ".git" in parts or "configs" in parts:
        continue
    rel = os.path.basename(os.path.dirname(path)) + "/" + os.path.basename(path)
    dst = os.path.join(dst_root, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(path, dst)
    count += 1
    print("copied:", rel)

print(f"total files: {count}")
if count == 0:
    for root, dirs, files in os.walk("/kaggle/input"):
        for f in files[:50]:
            print("INPUT:", os.path.join(root, f))
