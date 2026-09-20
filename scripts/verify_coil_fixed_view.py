"""Validate physics cues, framing and synchronization in the fixed-view scene."""
import json
import hashlib
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"scripts"))
from electromagnetism import coil_demo as demo
from electromagnetism.timing import map_time
from ammeter_checks import check_ammeter

scene = bpy.context.scene
timing = json.loads(scene["narration_timing"]) if "narration_timing" in scene else None
assert scene.frame_end == (timing["frames"] if timing else demo.DURATION*demo.FPS)
needles = [o for o in scene.objects if o.get("coil_compass_side")]
assert len(needles)==2
wire = next(o for o in scene.objects if "maximum_turns" in o)
assert demo.DENSE_RADIUS == demo.RADIUS and wire["axial_length"] == demo.LENGTH
assert all((a.co-Vector(b)).length<1e-5 for a,b in
           zip(wire.data.shape_keys.key_blocks["Twenty turns"].data,demo.dense_wire_points(1)))
rings = [o for o in scene.objects if o.get("branch_field_pair") and "guide_radius" in o]
assert len(rings)==12
local = [o for o in scene.objects if "local_winding_pair" in o and "guide_radius" in o]
assert len(local)==40
resultant = [o for o in scene.objects if "resultant_stage" in o]
assert [sum(o["resultant_stage"]==s for o in resultant) for s in range(3)] == [10,20,30]
camera = None
report = []
for source,amps,count,left in ((0,0,0,None),(8,.5,0,None),(24,.5,10,"N"),
        (29,0,0,None),(34,-.5,10,"S"),(53,0,0,None),(61,-.5,20,"S"),
        (70,0,0,None),(93,-.5,30,"S"),(100,0,0,None),(108,-.5,30,"S"),(114,0,0,None)):
    scene.frame_set(round(map_time(source,timing)*24)+1)
    bpy.context.view_layer.update()
    pose = tuple(v for row in scene.camera.matrix_world for v in row)
    if camera is None:
        camera = pose
    assert pose == camera, "Camera must remain fixed"
    check_ammeter(scene,amps,framed=True)
    assert sum(not o.hide_render for o in resultant)==count,(source,"field count")
    poles = [o for o in scene.objects if "pole" in o and not o.hide_render]
    assert len(poles)==(2 if left else 0)
    if left:
        assert next(o for o in poles if o["side"]=="left")["pole"]==left
    assert abs(needles[0].rotation_euler.z-needles[1].rotation_euler.z)<1e-5
    for needle in needles:
        assert abs(needle.rotation_euler.z-demo.needle_angle_at(source))<.005
    readings = [o for o in scene.objects if "display_degrees" in o and not o.hide_render]
    assert len(readings)==2 and readings[0]["display_degrees"]==readings[1]["display_degrees"]
    if source in (24,34):
        for obj in scene.objects:
            if obj.get("magnetic_field_arrow") and "arrowhead" in obj.name and not obj.hide_render:
                direction = obj.matrix_world.to_3x3()@Vector((0,0,1))
                _,field = demo.circuit_fields(tuple(obj.matrix_world.translation),1,demo.TURNS,demo.RADIUS)
                assert direction.dot(Vector(field)*amps)>0,(source,obj.name,"field arrow reversed")
    for obj in scene.objects:
        if obj.name.startswith(("Battery body","School science chalkboard","Switch state |")) and not obj.hide_render:
            for corner in obj.bound_box:
                uv = world_to_camera_view(scene,scene.camera,obj.matrix_world@Vector(corner))
                assert .005<uv.x<.995 and .005<uv.y<.995,(obj.name,tuple(uv),"clipped")
    # Each branch ring is perpendicular to its conductor. Its arrow follows
    # conventional current; reversal changes circulation without rotating wire.
    for ring in rings:
        if not amps:
            continue
        site = ring.parent
        normal = site.matrix_world.to_3x3()@Vector((1,0,0))
        points = [ring.matrix_world@Vector(p.co[:3]) for p in ring.data.splines[0].points]
        assert all(abs((p-site.location).dot(normal))<1e-5 for p in points),(source,ring.name,max(abs((p-site.location).dot(normal)) for p in points))
        if amps:
            arrow = next(o for o in scene.objects if o.parent==site and "chevron" in o.name)
            p = [arrow.matrix_world@Vector(q.co[:3]) for q in arrow.data.splines[0].points]
            expected = (-1 if amps>0 else 1)*normal.cross(p[1]-site.location)
            assert (p[1]-(p[0]+p[2])/2).dot(expected)>0
    report.append(dict(source_seconds=source,video_seconds=map_time(source,timing),
                       current_amperes=amps,field_lines=count,deflection_degrees=readings[0]["display_degrees"]))
clips = [o for o in scene.objects if o.get("paper_clip")]
for source,z in ((100,.035),(108,1.29),(114,.035)):
    scene.frame_set(round(map_time(source,timing)*24)+1)
    assert all(abs(o.location.z-z)<.005 for o in clips)
    for clip in clips:
        index = int(clip.name.rsplit(" ",1)[1])-1
        assert math.dist(tuple(clip.location)[:2],demo.clip_site(index))<1e-5
        assert abs(clip.location.x)-.11>demo.LENGTH/2, "Held clips must remain visible beyond the winding"
highlights = [o for o in scene.objects if o.get("application_highlight")]
assert len(highlights)==3
for source in (125,130,135.9):
    scene.frame_set(round(map_time(source,timing)*24)+1)
    assert all(not o.hide_render for o in highlights)
assert abs(map_time(136,timing)-map_time(125,timing)-11)<1e-6
assert all(image.packed_file for image in bpy.data.images if image.source=="FILE")
if timing:
    assert scene.sequence_editor.strips[0].sound.packed_file
    assert scene["narrator"] == "en-IN-PrabhatNeural"
name = "portable-fixed-view-verification.json" if Path(bpy.data.filepath).is_relative_to(ROOT/"archive") else "fixed-view-verification.json"
path = ROOT/"output/parts/02_coil_reversal"/name
path.write_text(json.dumps(dict(checks="passed",stages=report,scene=Path(bpy.data.filepath).name,
    scene_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()),indent=2)+"\n",encoding="utf-8")
print("PASS: fixed camera, two concentric rings, current circulation, three strengths, symmetric compasses, packed speech and 11-second applications.")
