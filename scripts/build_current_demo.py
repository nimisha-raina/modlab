"""Build Part 1 in Blender without rebuilding or replacing the opening lesson."""

from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism.current_chapter import build, DESTINATION

build()
target = DESTINATION / "compass_current.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print(f"PART_1_READY={target}", flush=True)
