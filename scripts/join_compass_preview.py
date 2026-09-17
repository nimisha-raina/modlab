"""Join separately rendered opening/compass sections without re-encoding.

Use the media environment (requirements-media.txt) after rendering the connected
project with --opening-only and then its compass scene with default arguments.
"""

import argparse
from pathlib import Path
import subprocess
import imageio_ffmpeg

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--full-quality", action="store_true")
args = parser.parse_args()
folder = Path(__file__).resolve().parents[1] / "output/parts/01_compass_current"
suffix = "_720p.mp4" if args.full_quality else "_preview.mp4"
names = ["opening"+suffix, "compass_current"+suffix]
for name in names:
    if not (folder / name).is_file():
        parser.error(f"Render {name} first")
list_path = folder / "preview-sections.txt"
list_path.write_text("".join(f"file '{name}'\n" for name in names), encoding="utf-8")
target = folder / ("opening_and_compass"+suffix)
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
                "-y", "-f", "concat", "-safe", "1", "-i", list_path.name,
                "-map", "0:v:0", "-c:v", "copy", "-an", "-movflags", "+faststart",
                target.name], cwd=folder, check=True)
print(f"CONNECTED_PREVIEW_READY={target}")
