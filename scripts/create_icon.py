"""Convert the approved Velide PNG into browser and Windows icon formats."""

import shutil
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parents[1]
folder = root / "desktop/assets"
folder.mkdir(parents=True, exist_ok=True)
for name in ("velide-logo.png", "baloide-logo.png"):
    shutil.copy2(root / "branding" / name, folder / name)
with Image.open(root / "branding/velide-logo.png") as source:
    image = source.convert("RGBA")
    image.save(
        folder / "velide.ico",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    for filename, size in [("favicon.png", 32), ("apple-touch-icon.png", 180)]:
        image.resize((size, size), Image.Resampling.LANCZOS).save(
            root / "backend/app/static" / filename
        )
