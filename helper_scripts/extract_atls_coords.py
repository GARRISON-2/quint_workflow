import json
import numpy as np
import cv2
from pathlib import Path
import requests

visuAlign_json = Path('')

with open(visuAlign_json) as f:
    data = json.load(f)

slice_data = data['slices'][0]
a = slice_data['anchoring']
ox, oy, oz = a[0], a[1], a[2]
ux, uy, uz = a[3], a[4], a[5]
vx, vy, vz = a[6], a[7], a[8]

width  = slice_data['width']
height = slice_data['height']

print(f"Slice: {slice_data['filename']}")
print(f"Origin (ox, oy, oz): {ox:.2f}, {oy:.2f}, {oz:.2f}")
print(f"U vector: {ux:.4f}, {uy:.4f}, {uz:.4f}")
print(f"V vector: {vx:.4f}, {vy:.4f}, {vz:.4f}")
print(f"Image size: {width} x {height}")
print(f"Number of markers: {len(slice_data['markers'])}")

# fetch atlas slice
url = (
    f"https://atlas.brain-map.org/atlas/svg_download"
    f"?atlas_id=1"
    f"&o={ox},{oy},{oz}"
    f"&u={ux},{uy},{uz}"
    f"&v={vx},{vy},{vz}"
    f"&width={width}&height={height}"
)

print(f"\nFetching atlas slice from Allen API...")
resp = requests.get(url, timeout=15)
resp.raise_for_status()
img_array = np.frombuffer(resp.content, dtype=np.uint8)
atlas_img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
print(f"Atlas image fetched: {atlas_img.shape}")

# marker canvas
markers = slice_data['markers']
src_x = [m[0] for m in markers]
src_y = [m[1] for m in markers]
dst_x = [m[2] for m in markers]
dst_y = [m[3] for m in markers]

marker_canvas = np.zeros((height, width, 3), dtype=np.uint8)
marker_canvas[:] = (46, 26, 26)  # #1a1a2e in BGR

# draw arrows and points
for sx, sy, dx, dy in zip(src_x, src_y, dst_x, dst_y):
    cv2.arrowedLine(marker_canvas, 
                    (int(sx), int(sy)), 
                    (int(dx), int(dy)), 
                    color=(0, 255, 255),  # yellow in BGR
                    thickness=1,
                    tipLength=0.02)

for sx, sy in zip(src_x, src_y):
    cv2.circle(marker_canvas, (int(sx), int(sy)), 3, (255, 255, 0), -1)  # cyan

for dx, dy in zip(dst_x, dst_y):
    cv2.circle(marker_canvas, (int(dx), int(dy)), 3, (0, 165, 255), -1)  # orange

# combine side by side — resize atlas to match marker canvas height
atlas_resized = cv2.resize(atlas_img[:, :, :3], (width, height))
combined = np.hstack([atlas_resized, marker_canvas])

cv2.imwrite('atlas_view.png', combined)
print("Saved to atlas_view.png")