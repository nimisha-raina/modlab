"""Render new pointers and resample reviewed frames onto the tutor timeline.

The apparatus tour has a stationary camera, so each pointer needs one new still.
Other frames sample the approved 12-fps review with nearest-frame selection;
no new laboratory geometry or lighting is introduced. The editable Blender
scene uses continuous keyframes on the same time map.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from electromagnetism.tutor_timing import source_time

PART = ROOT / "output/parts/01_compass_current"
FRAMES = PART / "tutor_review_frames"
VIDEO = PART / "opening_and_compass_tutor_review_720p.mp4"
FPS = 12


def render(reuse_highlights=False):
    lesson = json.loads((ROOT / "docs/first-case-narration.json").read_text())
    cues = json.loads((ROOT / lesson["audio_directory"] / "apparatus-cues.json").read_text())
    if not reuse_highlights:
        import bpy
        from electromagnetism.config import SCENE_NAME
        scene = bpy.data.scenes[SCENE_NAME]
        bpy.context.window.scene = scene
        scene.render.engine = "BLENDER_EEVEE"
        scene.render.use_sequencer = False
        scene.render.resolution_x, scene.render.resolution_y = 1280, 720
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.eevee.taa_render_samples = 8
    snapshots = {}
    for cue in cues:
        path = PART / ("highlight_" + cue["component"].replace(" ", "_") + ".png")
        if reuse_highlights:
            if not path.is_file():
                raise FileNotFoundError(f"Render the apparatus highlight first: {path}")
        else:
            scene.frame_set(round((cue["start"] + cue["end"]) / 2 * 24) + 1)
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
        snapshots[cue["component"]] = path
        print(f"TUTOR_HIGHLIGHT_READY={path.name}", flush=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    source_frames = PART / "complete_review_frames"
    assert len(list(source_frames.glob("frame_*.png"))) == 912, "Restore/render the reviewed source frames first."
    for index in range(round(lesson["duration"] * FPS)):
        time = index / FPS
        source = None
        if time < 10:
            frame = round(time * 24) + 1
            active = next((c for c in cues if round(c["start"] * 24)+1 <= frame < round(c["end"] * 24)+1), None)
            source = snapshots[active["component"]] if active else source_frames / "frame_00001.png"
        if source is None:
            old_frame = min(912, round(source_time(time) * FPS) + 1)
            source = source_frames / f"frame_{old_frame:05d}.png"
        shutil.copy2(source, FRAMES / f"frame_{index+1:05d}.png")
    report = {"duration":lesson["duration"], "frames":round(lesson["duration"]*FPS), "fps":FPS,
              "new_highlight_stills":0 if reuse_highlights else len(snapshots),
              "reused_highlight_stills":len(snapshots) if reuse_highlights else 0,
              "source_sampling":"nearest reviewed frame",
              "source_quantization_max_seconds":1/(2*FPS)}
    (PART / "tutor-render.json").write_text(json.dumps(report, indent=2)+"\n")
    print("TUTOR_REVIEW_FRAMES_READY", flush=True)


def encode():
    import subprocess
    import imageio_ffmpeg
    report = json.loads((PART / "tutor-render.json").read_text())
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
                    "-framerate", str(FPS), "-i", str(FRAMES / "frame_%05d.png"),
                    "-frames:v", str(report["frames"]), "-c:v", "libx264", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(VIDEO)], check=True)
    print(f"TUTOR_REVIEW_VIDEO={VIDEO}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encode", action="store_true")
    parser.add_argument("--reuse-highlights", action="store_true",
                        help="Reuse existing apparatus stills when only lesson timing changes.")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:] if "bpy" not in sys.modules else [])
    encode() if args.encode else render(args.reuse_highlights)
