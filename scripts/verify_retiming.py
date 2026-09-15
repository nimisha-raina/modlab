"""Exercise Blender retiming with a synthetic timeline; never save this scene.

Run against the un-narrated .blend. The temporary fixture stretches every
storyboard second to two seconds so existing geometry checks can detect missed
object, material, visibility, and camera keyframes. Audio is muted in this test.
"""
import json
from pathlib import Path
import runpy
import sys
import tempfile
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "src"))
from electromagnetism import narration
from electromagnetism.config import SCENE_NAME

scene = bpy.data.scenes[SCENE_NAME]
assert "narration_timing" not in scene, "Load the source timeline for this test."
script = json.loads((ROOT / "docs/narration.json").read_text())
fixture = {"duration":96,"fps":24,"frames":2304,"segments":[]}
for section in script["segments"]:
    fixture["segments"].append({**section,"target_start":section["start"]*2,
        "target_end":section["end"]*2,"audio":"output/audio/narration_00.mp3"})
with tempfile.TemporaryDirectory(prefix="em-retiming-") as temporary:
    narration.OUTPUT = Path(temporary)
    folder = Path(temporary) / "audio"
    folder.mkdir()
    (folder / "narration-timing.json").write_text(json.dumps(fixture))
    narration.attach(scene)
    for strip in scene.sequence_editor.strips:
        strip.volume = 0
    runpy.run_path(str(ROOT / "scripts/verify_scene.py"))
print("PASS: all scene checks also passed after retiming to 96 seconds. No file was saved.")
