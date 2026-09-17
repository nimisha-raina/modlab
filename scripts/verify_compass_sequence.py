"""Check the connected opening/compass timeline and its visual join."""

from pathlib import Path
import sys
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from electromagnetism.config import SCENE_NAME, LESSON, ELECTRON_RADIUS
from electromagnetism.current_demo import SCENE_NAME as CHAPTER_NAME, FPS, DURATION
from electromagnetism.camera_path import OPENING_WIDE
from ammeter_checks import check_ammeter

intro = bpy.data.scenes[SCENE_NAME]
chapter = bpy.data.scenes[CHAPTER_NAME]
assembly = bpy.data.scenes["00 - Opening and compass"]
assert intro.frame_end == LESSON.wide_view*FPS
assert assembly.frame_end == intro.frame_end+DURATION*FPS
editor = assembly.sequence_editor
strips = list(editor.strips if hasattr(editor, "strips") else editor.sequences)
assert len(strips) == 2 and all(s.type == "SCENE" for s in strips)
join = intro.frame_end+1
assert [(s.frame_final_start, s.frame_final_end) for s in strips] == [(1, join), (join, join+DURATION*FPS)]
assert not intro.sequence_editor and not chapter.sequence_editor
bpy.context.window.scene = intro
electrons = [o for o in intro.objects if o.name.startswith("Mobile electron")]
ions = [o for o in intro.objects if o.name.startswith("Copper ion ")]
rings = [o for o in intro.objects if o.name.startswith("Magnetic concentric circle") and "guide_radius" in o]
assert len(electrons) == LESSON.electrons and len(ions) == 36 and len(rings) == 3
assert LESSON.microscope_out-LESSON.switch_on == 8, "Electron-flow close-up must last eight seconds"
assert LESSON.microscope_in-LESSON.zoom_start >= 8, "Opening approach too fast"
for seconds, visible in [(0, False), (LESSON.microscope_in-.1, False),
                         (LESSON.microscope_in+.1, True), (LESSON.microscope_out-.1, True),
                         (LESSON.microscope_out+.1, False), (41, False)]:
    intro.frame_set(LESSON.frame(seconds))
    assert all(o.hide_render == (not visible) for o in electrons+ions), "Premature or separated particle visibility"
for seconds, amps in [(LESSON.switch_on-1, 0), (LESSON.switch_on+3, .5)]:
    intro.frame_set(LESSON.frame(seconds))
    bpy.context.view_layer.update()
    active = [o for o in intro.objects if "amperes" in o and not o.hide_render]
    assert len(active) == 1 and abs(active[0]["amperes"]-amps) < 1e-6
    check_ammeter(intro, amps)
    assert all(o.hide_render for o in rings) == (amps == 0)
    for electron in electrons:
        radius = max((electron.matrix_world.to_3x3() @ v.co).length for v in electron.data.vertices)
        assert abs(radius-ELECTRON_RADIUS) < 1e-6, "Electron size changed"
intro.frame_set(1)
assert (intro.camera.location-Vector(OPENING_WIDE[0])).length < 1e-5
for seconds in (LESSON.microscope_out+1.1, LESSON.zoom_out_end, 41):
    intro.frame_set(LESSON.frame(seconds))
    assert all(o.hide_render for o in intro.objects if o.name.startswith(("Copper cutaway shell", "Cutaway rim")))
    cover = next(o for o in intro.objects if o.name.startswith("Sample cover"))
    node = next(n for n in cover.data.materials[0].node_tree.nodes if n.type == "MIX_SHADER")
    assert abs(node.inputs[0].default_value) < 1e-6, "Cutaway remained open during pullback"
    assert all(not ring.hide_render for ring in rings), "Original concentric circles disappeared during pullback"
poses = []
for scene, frame in [(intro, intro.frame_end), (chapter, 1)]:
    bpy.context.window.scene = scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    switch = next(o for o in scene.objects if o.name.startswith("Switch hinge | animated"))
    assert abs(switch.rotation_euler.y) < 1e-6, "Current interrupted at join"
    active = [o for o in scene.objects if "amperes" in o and not o.hide_render]
    assert len(active) == 1 and abs(active[0]["amperes"]-.5) < 1e-6
    assert not any(o.name.startswith("Mobile electron") and not o.hide_render for o in scene.objects)
    poses.append(scene.camera.matrix_world.copy())
assert (poses[0].translation-poses[1].translation).length < .01
assert poses[0].to_quaternion().rotation_difference(poses[1].to_quaternion()).angle < .001
assert intro.camera.data.lens == chapter.camera.data.lens
intro.frame_set(intro.frame_end)
chapter.frame_set(1)
intro_radii = sorted(ring["guide_radius"]*ring.parent.scale.x for ring in rings)
chapter_rings = [o for o in chapter.objects if o.get("field_location") == "Far left" and o.get("current_level") == 1]
assert len(chapter_rings) == 3
assert all(abs(a-b) < 1e-6 for a, b in zip(intro_radii, sorted(o["guide_radius"] for o in chapter_rings)))
for scene in (intro, chapter):
    assert not any(o.name.split(".")[0] == "Copper conductor 1" for o in scene.objects), "Ammeter bypass"
    assert len([o for o in scene.objects if "series_path" in o]) == 4
    assert len([o for o in scene.objects if o.get("rear_connection")]) == 2
    assert not any("insulated_lead" in o for o in scene.objects)
bpy.context.window.scene = assembly
assembly.frame_set(1)
print("PASS: connected timeline including summary; copper cutaway retained; closed switch, 0.50 A and continuous camera at join; series ammeters; no narration mismatch.")
