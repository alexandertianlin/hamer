"""Direct download using requests with resume support"""
import os, sys, time
import requests

BASE = r"D:\hamer_data"
os.makedirs(BASE, exist_ok=True)
TAR_PATH = os.path.join(BASE, "hamer_demo_data.tar.gz")
URL = "https://drive.google.com/uc?id=1mv7CUAnm73oKsEEG1xE3xH2C_oqcFSzT"

# First get the real download URL via gdown
print("Getting download link ...")
import gdown
real_url = gdown.get_url_from_id("1mv7CUAnm73oKsEEG1xE3xH2C_oqcFSzT")
if not real_url:
    real_url = URL

# Download with requests (streaming, better connection handling)
print(f"Downloading {TAR_PATH} ...")
resp = requests.get(real_url, stream=True, timeout=30)
total = int(resp.headers.get('content-length', 0))
downloaded = 0
t0 = time.time()

with open(TAR_PATH, 'wb') as f:
    for chunk in resp.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                pct = downloaded / total * 100
                elapsed = time.time() - t0
                speed = downloaded / elapsed / 1024 / 1024
                eta = (total - downloaded) / downloaded * elapsed / 60 if downloaded > 0 else 0
                sys.stdout.write(f"\r{pct:.1f}% | {downloaded/1024**3:.2f}/{total/1024**3:.2f} GB | {speed:.1f} MB/s | ETA {eta:.0f} min")
                sys.stdout.flush()

if os.path.exists(TAR_PATH):
    sz = os.path.getsize(TAR_PATH)
    print(f"\nDone! {sz/1024**3:.2f} GB")
else:
    print("\nDownload failed")
    sys.exit(1)
