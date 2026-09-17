"""Render every frame of the complete first case, reusing identical stills.

The output is a 1280x720, 12-fps silent review at the lesson's source timing.
The editable scenes keep their 24-fps settings. Identical visible states reuse
a PNG, preserving their full duration while avoiding repeated static renders.
Use the media environment with --encode after the Blender render finishes.
"""

import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from electromagnetism.config import SCENE_NAME, LESSON
from electromagnetism import current_demo as demo

DESTINATION = ROOT / "output/parts/01_compass_current"
FRAMES = DESTINATION / "complete_review_frames"
VIDEO = DESTINATION / "opening_and_compass_review_720p.mp4"
REVIEW_FPS = 12


def visible_state(scene):
    """Track evaluated poses, text, deformation and animated shader inputs."""
    state = []
    materials = set()
    for obj in scene.objects:
        if obj.hide_render:
            continue
        state.append((obj.name, tuple(round(v, 7) for row in obj.matrix_world for v in row)))
        if obj.type == "FONT":
            state.append((obj.data.body, obj.data.size))
        if obj.type == "LIGHT":
            state.append((obj.data.energy, tuple(obj.data.color)))
        if obj.type == "CURVE":
            state.append((obj.data.bevel_factor_start, obj.data.bevel_factor_end))
        data = obj.data
        keys = getattr(data, "shape_keys", None)
        if keys:
            state.append(tuple(key.value for key in keys.key_blocks))
        materials.update(slot.material for slot in obj.material_slots if slot.material)
    for material in sorted(materials, key=lambda m: m.name):
        tree = material.node_tree
        if not tree or not tree.animation_data:
            continue
        for node in tree.nodes:
            for socket in node.inputs:
                value = getattr(socket, "default_value", None)
                if isinstance(value, (int, float)):
                    state.append((material.name, node.name, socket.name, round(value, 7)))
                elif value is not None:
                    try:
                        state.append(tuple(round(v, 7) for v in value))
                    except TypeError:
                        pass
    return tuple(state)


def render(stills_only=False):
    import os
    import bpy
    print(f"COMPLETE_REVIEW_RENDER_PID={os.getpid()}", flush=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    count = rendered = reused = 0
    priority_cache = {}
    checks = [(SCENE_NAME, 0, "opening_board_circuit"),
              (SCENE_NAME, 7, "slow_approach"),
              (SCENE_NAME, 32, "persistent_circles"),
              (SCENE_NAME, 41, "wide_ammeter"),
              (demo.SCENE_NAME, 0, "compass_join"),
              (demo.SCENE_NAME, 8, "reading_050A"),
              (demo.SCENE_NAME, 18, "reading_100A"),
              (demo.SCENE_NAME, 25, "summary_return"),
              (demo.SCENE_NAME, 28, "summary_board")]
    for scene_name, seconds, name in checks:
        scene = bpy.data.scenes[scene_name]
        bpy.context.window.scene = scene
        scene.render.engine = "BLENDER_EEVEE"
        scene.render.use_sequencer = False
        scene.render.resolution_x, scene.render.resolution_y = 1280, 720
        scene.render.resolution_percentage = 100
        scene.eevee.taa_render_samples = 8
        scene.render.image_settings.file_format = "PNG"
        scene.frame_set(round(seconds*demo.FPS)+1)
        bpy.context.view_layer.update()
        target = DESTINATION / (name+"_720p.png")
        scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True)
        priority_cache[(scene.name, visible_state(scene))] = target
        print(f"COMPLETE_REVIEW_STILL={target.name}", flush=True)
    if stills_only:
        print("COMPLETE_REVIEW_STILLS_READY", flush=True)
        return
    for name in (SCENE_NAME, demo.SCENE_NAME):
        scene = bpy.data.scenes[name]
        bpy.context.window.scene = scene
        scene.render.engine = "BLENDER_EEVEE"
        scene.render.use_sequencer = False
        scene.render.resolution_x, scene.render.resolution_y = 1280, 720
        scene.render.resolution_percentage = 100
        scene.eevee.taa_render_samples = 8
        scene.render.image_settings.file_format = "PNG"
        previous = previous_file = None
        for frame in range(1, scene.frame_end+1, demo.FPS//REVIEW_FPS):
            count += 1
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            state = visible_state(scene)
            target = FRAMES / f"frame_{count:05d}.png"
            priority_file = priority_cache.get((scene.name, state))
            if priority_file:
                shutil.copyfile(priority_file, target)
                reused += 1
            elif state == previous:
                shutil.copyfile(previous_file, target)
                reused += 1
            else:
                scene.render.filepath = str(target)
                bpy.ops.render.render(write_still=True)
                rendered += 1
            previous, previous_file = state, target
            print(f"COMPLETE_REVIEW_FRAME={count} SOURCE={name} TIME={(frame-1)/demo.FPS:.2f} RENDERED={rendered} REUSED={reused}", flush=True)
    expected = round((LESSON.wide_view+demo.DURATION)*REVIEW_FPS)
    assert count == expected
    (DESTINATION / "complete-review-render.json").write_text(json.dumps({
        "frames": count, "rendered_frames": rendered, "reused_frames": reused,
        "fps": REVIEW_FPS, "size": [1280, 720],
        "duration_seconds": count/REVIEW_FPS, "audio_streams": 0,
    }, indent=2)+"\n", encoding="utf-8")
    print("COMPLETE_REVIEW_RENDER_READY", flush=True)


def encode():
    import subprocess
    import imageio_ffmpeg
    report = json.loads((DESTINATION / "complete-review-render.json").read_text())
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
                    "-y", "-framerate", str(REVIEW_FPS), "-start_number", "1",
                    "-i", str(FRAMES / "frame_%05d.png"), "-frames:v", str(report["frames"]),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(VIDEO)],
                   check=True)
    print(f"COMPLETE_REVIEW_VIDEO={VIDEO}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encode", action="store_true")
    parser.add_argument("--stills-only", action="store_true", help="Render apparatus and transition checks before the full export")
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:] if "bpy" not in sys.modules else []
    args = parser.parse_args(argv)
    encode() if args.encode else render(args.stills_only)
