import urllib.request, os, zipfile
url = "https://codeload.github.com/alexandertianlin/Gesture-glove-UI-unity/zip/refs/heads/main"
zip_path = r"D:\Gesture-glove-UI-unity.zip"
out_dir = r"D:\Gesture-glove-UI-unity"
print("Downloading ...")
try:
    urllib.request.urlretrieve(url, zip_path)
    sz = os.path.getsize(zip_path)
    print(f"Downloaded {sz/1024:.0f} KB")
    with zipfile.ZipFile(zip_path, "r") as zf:
        for m in zf.namelist():
            parts = m.split("/", 1)
            if len(parts) > 1:
                dst = os.path.join(out_dir, parts[1])
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if not m.endswith("/"):
                    zf.extract(m, out_dir)
                    # Move from Gesture-glove-UI-unity-main/* to root
                    src = os.path.join(out_dir, m)
                    if os.path.exists(src):
                        os.renames(src, dst)
        # Cleanup temp dir
        temp_dir = os.path.join(out_dir, "Gesture-glove-UI-unity-main")
        if os.path.exists(temp_dir):
            import shutil; shutil.rmtree(temp_dir)
    os.remove(zip_path)
    file_count = sum(len(fs) for _,_,fs in os.walk(out_dir))
    print(f"Extracted {file_count} files to {out_dir}")
except Exception as e:
    print(f"Failed: {e}")
