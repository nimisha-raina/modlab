"""Render the saved lesson for the web. Run through Blender after loading it.

blender --background output/electromagnetism_intro.blend \
  --python scripts/render_video.py -- --probe

The saved .blend is not modified. EEVEE provides a practical classroom-video
render; the original project still uses Cycles for its polished stills.
"""

import argparse
from pathlib import Path
import sys
import time
import bpy

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--probe", action="store_true")
parser.add_argument("--probe-frame", type=int, default=577)
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
scene = bpy.data.scenes["01 - Electricity makes magnetism"]
bpy.context.window.scene = scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
    scene.eevee.taa_render_samples = 32
destination = root / "output" / "video"
destination.mkdir(exist_ok=True)
start = time.monotonic()
if args.probe:
    scene.frame_set(args.probe_frame)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(destination / f"eevee_probe_{args.probe_frame:04}.png")
    bpy.ops.render.render(write_still=True)
    print(f"PROBE_SECONDS={time.monotonic()-start:.2f}", flush=True)
else:
    if hasattr(scene.render.image_settings, "media_type"):
        scene.render.image_settings.media_type = "VIDEO"
    else:
        scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.audio_codec = "AAC"
    scene.render.ffmpeg.audio_bitrate = 160
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.filepath = str(destination / "electromagnetism.mp4")
    bpy.ops.render.render(animation=True)
    print(f"VIDEO_READY={scene.render.filepath}", flush=True)
    print(f"RENDER_SECONDS={time.monotonic()-start:.2f}", flush=True)
