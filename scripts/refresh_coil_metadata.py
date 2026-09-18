"""Refresh non-visual science notes stored in the reviewed coil scene."""

from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from electromagnetism import coil_demo as demo


scene = bpy.data.scenes[demo.SCENE_NAME]
scene["physics"] = (
    "10 then 20 turns; complete-circuit fields; ideal symmetric end-compass "
    "comparison with one common Earth field; illustrative core gain."
)
scene["field_guides"] = (
    "Paired local circles; axisymmetric finite-ring approximation in several "
    "planes; closed resultant loops; drawing density is illustrative."
)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("COIL_METADATA_REFRESHED")
