"""Export the loaded lesson with packed audio and relative asset paths.

Run through Blender after opening output/electromagnetism_intro.blend.
The shared scene is written to assets/scene/electromagnetism_intro.blend.
"""

from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
destination = ROOT / "assets/scene/electromagnetism_intro.blend"
destination.parent.mkdir(parents=True, exist_ok=True)
for sound in bpy.data.sounds:
    name = Path(sound.filepath).name
    assert (ROOT / "assets/narration" / name).is_file(), f"Missing reference audio: {name}"
    if not sound.packed_file:
        sound.pack()
    sound.filepath = "//../narration/" + name
for scene in bpy.data.scenes:
    scene.render.filepath = "//../../output/frames/lesson_"
# Workspaces can retain the original computer's file-browser directory.
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type == "FILE_BROWSER" and space.params:
                # Overwrite the fixed-size buffer before shortening it; Blender
                # otherwise retains bytes beyond the new string terminator.
                space.params.directory = b"/" * 1023
                space.params.directory = b"//"
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(destination), relative_remap=False, compress=True)
print("Portable scene exported with packed narration and relative media paths.")
