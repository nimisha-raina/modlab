"""Copy the finished narrated Blender render and matching timing to the site."""
import json
from pathlib import Path
import shutil
import subprocess
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "student-lesson"
timing = ROOT / "output/audio/narration-timing.json"
info = json.loads((ROOT / "output/build-info.json").read_text())
speech = json.loads(timing.read_text())
assert info["frames"] == speech["frames"], "Rebuild Blender after preparing narration."
shutil.copy2(ROOT / "output/video/electromagnetism.mp4", SITE / "dist/assets/electromagnetism.mp4")
shutil.copy2(timing,SITE / "content/narration-timing.json")
shutil.copy2(ROOT / "output/web-captions.json",SITE / "content/captions.json")
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),"-hide_banner","-loglevel","error","-y",
                "-i",str(SITE / "dist/assets/electromagnetism.mp4"),"-frames:v","1",
                "-q:v","2",str(SITE / "dist/assets/poster.jpg")], check=True)
print(f"Student lesson media synchronized: {speech['duration']:.2f} seconds")
