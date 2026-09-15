"""Open this file in Blender's Text Editor and press Run Script (Alt/Option+P).

Terminal alternative:
    blender --background --python run.py -- --quality preview --render-stills

bpy is supplied by Blender. Do not pip-install it into your normal Python.
"""

import argparse
from pathlib import Path
import sys


def main():
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root / "src"))
    # Running this file again in Blender also picks up edits to helper modules.
    for module in list(sys.modules):
        if module == "electromagnetism" or module.startswith("electromagnetism."):
            del sys.modules[module]

    try:
        import bpy
    except ModuleNotFoundError:
        raise SystemExit("Run this script through Blender. See README.md for exact steps.")

    from electromagnetism.build import build_lesson
    from electromagnetism.config import OUTPUT, LESSON

    parser = argparse.ArgumentParser(description="Build the Class 8 electromagnetism lesson")
    parser.add_argument("--quality", choices=("preview", "final"), default="preview")
    parser.add_argument("--render-stills", action="store_true", help="Render six storyboard images")
    parser.add_argument("--render-frame", type=int, help="Render just one frame")
    parser.add_argument("--render-animation", action="store_true", help="Render all frames as PNGs")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])

    scene = build_lesson(args.quality)
    if args.render_frame is not None and not scene.frame_start <= args.render_frame <= scene.frame_end:
        parser.error(f"--render-frame must be between {scene.frame_start} and {scene.frame_end}")
    blend_path = OUTPUT / "electromagnetism_intro.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print(f"\nREADY: {blend_path}\n")

    original_path = scene.render.filepath
    if args.render_stills or args.render_frame is not None:
        destination = OUTPUT / "stills_v2"
        destination.mkdir(parents=True, exist_ok=True)
        frames = [LESSON.frame(s) for s in (0, 7, 16, 24, 32, 41)] if args.render_stills else [args.render_frame]
        for frame in frames:
            scene.frame_set(frame)
            scene.render.filepath = str(destination / f"frame_{frame:04}.png")
            bpy.ops.render.render(write_still=True)
        scene.render.filepath = original_path
        scene.frame_set(1)
    if args.render_animation:
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
