"""Prepare working media from included assets; preserve existing work by default."""

import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def restore(overwrite=False):
    pairs = []
    for folder, target in [("narration", "audio"), ("reference", "")]:
        for source in sorted((ROOT / "assets" / folder).iterdir()):
            if source.is_file():
                pairs.append((source, ROOT / "output" / target / source.name))
    current = ROOT / "assets/first-case-narration"
    if current.exists():
        pairs.extend((source, ROOT / "output/parts/01_compass_current/audio" / source.name)
                     for source in sorted(current.iterdir()) if source.is_file())
    tutor = ROOT / "assets/tutor-narration"
    if tutor.exists():
        pairs.extend((source, ROOT / "output/parts/01_compass_current/audio_tutor" / source.name)
                     for source in sorted(tutor.iterdir()) if source.is_file())
    pairs.append((ROOT / "student-lesson/dist/assets/electromagnetism.mp4",
                  ROOT / "output/parts/01_compass_current/opening_and_compass_narrated_720p.mp4"))
    copied = 0
    for source, target in pairs:
        if target.exists() and not overwrite:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied += 1
    print(f"Prepared {copied} working files. Build the scene in Blender using run.py.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true",
                        help="Replace working media and timing with reference assets")
    restore(parser.parse_args().overwrite)
