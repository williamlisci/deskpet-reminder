from PIL import Image
import os
import numpy as np

SRC_DIR = "assets/cat_raw"
DST_DIR = "assets/cat"
THRESHOLD = 240

os.makedirs(DST_DIR, exist_ok=True)
files = ["sit.png", "walk.png", "jump.png"]

for filename in files:
    src_path = os.path.join(SRC_DIR, filename)
    if not os.path.exists(src_path):
        print(f"⚠️  File not found: {src_path}")
        continue

    img = Image.open(src_path).convert("RGBA")
    arr = np.array(img)

    # Make near-white pixels transparent
    white_mask = np.all(arr[:, :, :3] > THRESHOLD, axis=2)
    arr[white_mask, 3] = 0

    img = Image.fromarray(arr)
    img = img.resize((48, 48), Image.Resampling.LANCZOS)

    img.save(os.path.join(DST_DIR, filename))
    print(f"✅ Đã xử lý: {filename}")

print("🎉 Hoàn thành!")
