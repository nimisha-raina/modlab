"""Decode a silent compass preview and check its duration and frame timing.

Run with the media environment (requirements-media.txt). This checks encoded
media, while the Blender verifiers check scene behavior. Visual review remains
necessary for readability and appearance.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import av

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))
from electromagnetism.current_demo import DURATION, FPS
from electromagnetism.config import LESSON

parser = argparse.ArgumentParser(description=__doc__)
selection = parser.add_mutually_exclusive_group()
selection.add_argument("--combined", action="store_true")
selection.add_argument("--opening-only", action="store_true")
selection.add_argument("--coil", action="store_true")
parser.add_argument("--draft-fps", type=int, choices=(4, 6, 12), default=12)
parser.add_argument("--width",type=int,choices=(640,1280),help="Width used by the efficient visual-review renderer")
parser.add_argument("--full-quality", action="store_true")
parser.add_argument("--review-720p", action="store_true", help="Check a complete 12-fps 720p visual review")
parser.add_argument("--range", type=float, nargs=2, metavar=("START", "END"),
                    help="Check a separately rendered source-time interval")
args = parser.parse_args()
folder = root / "output/parts/01_compass_current"
if args.coil:
    from electromagnetism.coil_demo import DURATION
    folder = root / "output/parts/02_coil_reversal"
basename = "coil_reversal" if args.coil else "opening_and_compass" if args.combined else "opening" if args.opening_only else "compass_current"
suffix = "_720p.mp4" if args.full_quality else "_preview.mp4" if args.draft_fps == 12 else f"_draft_{args.draft_fps}fps.mp4"
if args.review_720p:
    if not (args.combined or args.coil) or args.full_quality or args.draft_fps != 12 or args.range:
        parser.error("720p review requires --combined or --coil, 12 fps and the full interval")
    suffix = "_review_720p.mp4"
duration = LESSON.wide_view if args.opening_only else DURATION + (LESSON.wide_view if args.combined else 0)
fps = FPS if args.full_quality else args.draft_fps
if args.range:
    start, end = args.range
    if not 0 <= start < end <= duration:
        parser.error("Movie range must lie within the scene")
    if any(abs(t*fps-round(t*fps)) > 1e-6 for t in args.range):
        parser.error("Range endpoints must align with the review frame rate")
    basename += f"_segment_{start:05.1f}-{end:05.1f}"
    duration = end-start
path = folder / (basename + suffix)
width = 1280 if args.full_quality or args.review_720p else args.width or 640
size = (width,round(width*9/16))
with av.open(str(path)) as media:
    assert len(media.streams.video) == 1
    assert not media.streams.audio, "This visual draft must be silent"
    stream = media.streams.video[0]
    assert stream.average_rate == fps
    assert (stream.width, stream.height) == size
    encoded_duration = float(stream.duration*stream.time_base)
    assert abs(encoded_duration-duration) < 1/fps
    frames = 0
    previous = None
    for frame in media.decode(stream):
        time = float(frame.time)
        if previous is None:
            assert abs(time) < 1e-5
        else:
            assert abs(time-previous-1/fps) < 1e-5, "Irregular frame timestamps"
        frames += 1
        previous = time
    assert frames == round(duration*fps), (frames, duration, fps)
with path.open("rb") as file:
    digest = hashlib.file_digest(file, "sha256").hexdigest()
report = {"file": path.name, "sha256": digest, "frames": frames, "fps": fps,
          "duration_seconds": encoded_duration, "size": size, "audio_streams": 0}
if args.range:
    report["source_interval_seconds"] = args.range
report_name = "connected-preview-validation" if args.combined else "opening-preview-validation" if args.opening_only else "preview-validation"
report_suffix = "" if args.full_quality or args.draft_fps == 12 else f"-{args.draft_fps}fps"
if args.review_720p:
    report_suffix = "-review-720p"
if args.range:
    report_suffix += f"-segment-{start:05.1f}-{end:05.1f}"
report_path = folder / (report_name+report_suffix+".json")
report_path.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, indent=2))
print("PASS: complete silent preview; expected duration, dimensions and regular frame timestamps.")
