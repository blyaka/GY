from PIL import Image
import os

input_dir = "static/images"
output_dir = "static/images/optimized"
os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(input_dir):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        img = Image.open(os.path.join(input_dir, file))
        # ресайз до 1600 по ширине
        img.thumbnail((1600, 1600))
        base, _ = os.path.splitext(file)
        out_file = os.path.join(output_dir, base + ".webp")
        img.save(out_file, "WEBP", quality=70, method=6)
        print(f"Saved {out_file}")
