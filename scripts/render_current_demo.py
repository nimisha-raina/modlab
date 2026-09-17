"""Render review stills or silent MP4s from saved laboratory case scenes.

Use --stills 0 8 11 18 for layout checks. The default movie is a 640x360,
12-fps draft; --full-quality uses the scene's 1280x720, 24-fps timeline.
Rendering never saves over the editable .blend or the original lesson video.
"""

import argparse
from pathlib import Path
import sys
import time
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism import current_demo as demo
from electromagnetism.config import SCENE_NAME as INTRO_NAME
from electromagnetism.current_chapter import DESTINATION

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--stills", type=float, nargs="+")
parser.add_argument("--full-quality", action="store_true")
selection = parser.add_mutually_exclusive_group()
selection.add_argument("--combined", action="store_true", help="Render the opening-and-compass assembly")
selection.add_argument("--opening-only", action="store_true", help="Render just the opening from the connected project")
selection.add_argument("--coil", action="store_true", help="Render the independent coil and reversal case")
parser.add_argument("--draft-fps", type=int, choices=(4, 6, 12), default=12,
                    help="Frame rate for a small visual review; full quality remains 24 fps")
parser.add_argument("--movie", action="store_true", help="Also render the movie after requested stills")
parser.add_argument("--range", type=float, nargs=2, metavar=("START", "END"),
                    help="Render only this source-time interval to a separate segment movie")
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
if args.coil:
    from electromagnetism import coil_demo
    from electromagnetism.coil_chapter import DESTINATION
    scene_name, basename = coil_demo.SCENE_NAME, "coil_reversal"
elif args.combined:
    scene_name, basename = "00 - Opening and compass", "opening_and_compass"
elif args.opening_only:
    scene_name, basename = INTRO_NAME, "opening"
else:
    scene_name, basename = demo.SCENE_NAME, "compass_current"
scene = bpy.data.scenes[scene_name]
bpy.context.window.scene = scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = (1280, 720) if args.full_quality else (640, 360)
scene.render.resolution_percentage = 100
scene.render.use_sequencer = args.combined
if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
    scene.eevee.taa_render_samples = 32 if args.full_quality else 8
DESTINATION.mkdir(parents=True, exist_ok=True)
if args.combined:
    for source in bpy.data.scenes:
        if source != scene:
            source.render.engine = "BLENDER_EEVEE"
            source.render.resolution_x = scene.render.resolution_x
            source.render.resolution_y = scene.render.resolution_y
            source.render.resolution_percentage = 100
            if hasattr(source, "eevee") and hasattr(source.eevee, "taa_render_samples"):
                source.eevee.taa_render_samples = 32 if args.full_quality else 8
duration = scene.frame_end/demo.FPS
if args.range:
    range_start, range_end = args.range
    review_fps = demo.FPS if args.full_quality else args.draft_fps
    if not 0 <= range_start < range_end <= duration:
        parser.error("Movie range must lie within the scene")
    if any(abs(t*review_fps-round(t*review_fps)) > 1e-6 for t in args.range):
        parser.error("Range endpoints must align with the selected review frame rate")
prefix = "connected_" if args.combined else "opening_" if args.opening_only else ""
start = time.monotonic()
if args.stills is not None:
    if any(not 0 <= t < duration for t in args.stills):
        parser.error("Still times must lie within the chapter")
    scene.render.image_settings.file_format = "PNG"
    for seconds in args.stills:
        scene.frame_set(round(seconds*demo.FPS)+1)
        scene.render.filepath = str(DESTINATION / f"{prefix}review_{seconds:05.1f}s.png")
        bpy.ops.render.render(write_still=True)
if args.stills is None or args.movie:
    if hasattr(scene.render.image_settings, "media_type"):
        scene.render.image_settings.media_type = "VIDEO"
    else:
        scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.audio_codec = "NONE"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.frame_step = 1 if args.full_quality else demo.FPS//args.draft_fps
    scene.render.fps = demo.FPS//scene.frame_step
    suffix = "_720p.mp4" if args.full_quality else "_preview.mp4" if args.draft_fps == 12 else f"_draft_{args.draft_fps}fps.mp4"
    if args.range:
        scene.frame_start = round(range_start*demo.FPS)+1
        scene.frame_end = round(range_end*demo.FPS)
        basename += f"_segment_{range_start:05.1f}-{range_end:05.1f}"
    scene.render.filepath = str(DESTINATION / (basename+suffix))
    bpy.ops.render.render(animation=True)
print(f"REVIEW_RENDER_SECONDS={time.monotonic()-start:.2f}", flush=True)
