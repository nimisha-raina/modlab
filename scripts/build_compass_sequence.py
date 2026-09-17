"""Assemble the wide copper opening and compass continuation.

The silent visual timeline ends the opening at source second 42, keeping the
switch closed. The separate original reference build and media are preserved.
"""

import argparse
from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism.build import build_lesson, clean_previous_lesson
from electromagnetism.current_chapter import build, DESTINATION
from electromagnetism.config import LESSON, SCENE_NAME
from electromagnetism.current_demo import DURATION, FPS

ASSEMBLY_NAME = "00 - Opening and compass"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--reuse-opening", action="store_true",
                    help="Rebuild only the continuation in a loaded connected project")
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
if args.reuse_opening:
    intro = bpy.data.scenes[SCENE_NAME]
    assert intro.frame_end == LESSON.wide_view*FPS and not intro.sequence_editor
    assert intro["switch_on_frame"] == LESSON.frame(LESSON.switch_on), "Rebuild the opening to apply the revised timing and persistent circles."
    assert len([o for o in intro.objects if "series_path" in o]) == 4
    assert len([o for o in intro.objects if o.get("rear_connection")]) == 2, "Rebuild the opening to apply concealed meter connections."
else:
    intro = build_lesson(attach_audio=False, series_ammeter=True, export_files=False)
intro.frame_end = round(LESSON.wide_view*FPS)
intro.render.use_sequencer = False
intro["assembly_note"] = "Cut at completed zoom-out; current stays on for compass placement."
for marker in list(intro.timeline_markers):
    if marker.frame > intro.frame_end:
        intro.timeline_markers.remove(marker)
clean_previous_lesson(ASSEMBLY_NAME)
chapter = build()
chapter.render.use_sequencer = False
for source in (intro, chapter):
    source.render.engine = "BLENDER_EEVEE"
    source.eevee.taa_render_samples = 8
# A reused assembly starts in the sequencer. Give the separate chapter file
# its camera view before saving, then restore a sequence preview below.
model_areas = [area for area in bpy.context.window.screen.areas
               if area.type in {"VIEW_3D", "SEQUENCE_EDITOR"}]
if model_areas:
    model_view = max(model_areas, key=lambda area: area.width*area.height)
    model_view.type = "VIEW_3D"
    model_view.spaces.active.region_3d.view_perspective = "CAMERA"
    model_view.spaces.active.shading.type = "MATERIAL"
# Keep the chapter file current as well as the connected assembly. Its active
# scene is the independently playable continuation; no reference media is saved.
DESTINATION.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(DESTINATION / "compass_current.blend"))
assembly = bpy.data.scenes.new(ASSEMBLY_NAME)
assembly.render.fps = FPS
assembly.render.resolution_x = 1280
assembly.render.resolution_y = 720
assembly.render.resolution_percentage = 100
assembly.frame_end = intro.frame_end+DURATION*FPS
assembly.view_settings.view_transform = intro.view_settings.view_transform
editor = assembly.sequence_editor_create()
strips = editor.strips if hasattr(editor, "strips") else editor.sequences
for name, scene, start in [("Opening | copper cutaway and zoom-out", intro, 1),
                            ("Compass placement and current doubling", chapter, intro.frame_end+1)]:
    strip = strips.new_scene(name, scene, channel=1, frame_start=start)
    strip.scene_input = "CAMERA"
    strip.frame_final_end = start+scene.frame_end
assembly.render.use_sequencer = True
assembly["audio_status"] = "Silent visual assembly; final narration requires revised speech and timing."
assembly["opening_seconds"] = LESSON.wide_view
assembly["chapter_seconds"] = DURATION
assembly.timeline_markers.new("Place compass | current remains on", frame=intro.frame_end+1)
assembly.timeline_markers.new("Double current | ammeter 1.00 A", frame=intro.frame_end+14*FPS+1)
bpy.context.window.scene = assembly
assembly.frame_set(1)
view_areas = [area for area in bpy.context.window.screen.areas if area.type == "VIEW_3D"]
if view_areas:
    preview = max(view_areas, key=lambda area: area.width*area.height)
    preview.type = "SEQUENCE_EDITOR"
    preview.spaces.active.view_type = "PREVIEW"
DESTINATION.mkdir(parents=True, exist_ok=True)
target = DESTINATION / "opening_and_compass.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print(f"CONNECTED_SEQUENCE_READY={target}", flush=True)
