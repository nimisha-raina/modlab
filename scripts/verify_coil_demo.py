"""Validate the complete coil, reversal, iron-core and paper-clip case."""
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from electromagnetism import coil_demo as demo
from electromagnetism.coil_board import SUMMARY
from electromagnetism.field_layout import with_ammeter
from ammeter_checks import check_ammeter
scene = bpy.data.scenes[demo.SCENE_NAME]
bpy.context.window.scene = scene
assert scene.frame_end == demo.FPS*demo.DURATION and scene.render.fps == 24
wire = next(o for o in scene.objects if "maximum_turns" in o)
assert wire.type == "CURVE" and abs(wire.data.bevel_depth-demo.WIRE_RADIUS)<1e-6
assert wire["axial_length"] == demo.LENGTH
keys = wire.data.shape_keys
assert not keys.use_relative
for name,points in (("Basis",demo.wire_points(1)),("Twenty turns",demo.dense_wire_points(1))):
    assert all((p.co-Vector(q)).length<1e-6 for p,q in zip(keys.key_blocks[name].data,points))
guides = [o for o in scene.objects if o.get("field_guide")]
extra = [o for o in scene.objects if o.get("strength_stage")]
assert len(guides)==10 and len(extra)==18
lower = [o for o in scene.objects if o.get("local_lower_field")]
upper = [o for o in scene.objects if o.get("upper_winding_field")]
assert len(lower)==20 and len(upper)==20, "Each shown turn location needs two concentric circles"
branch_rings = [o for o in scene.objects if o.get("branch_field_pair") and o.get("guide_radius")]
assert len(branch_rings)==12, "Six circuit sites need two concentric circles each"
current_arrows = [o for o in scene.objects if o.get("conventional_current_arrow")]
assert current_arrows
needles = sorted([o for o in scene.objects if o.get("coil_compass_side")],key=lambda o:o["coil_compass_side"])
assert len(needles)==2
clips = [o for o in scene.objects if o.get("paper_clip")]
assert len(clips)==6
regions = [o for o in scene.objects if o.get("magnetic_region")]
assert len(regions)==10
switch = next(o for o in scene.objects if o.name.startswith("Switch hinge"))
cell = next(o for o in scene.objects if o.name.startswith("Cell | Reverse connections"))
for seconds,amps,count,left_pole in ((0,0,0,None),(5,0,0,None),(26,.5,10,"N"),
                                   (29,0,0,None),(35,-.5,10,"S"),(53,0,0,None),
                                   (61,-.5,16,"S"),(70,0,0,None),(93,-.5,28,"S"),
                                   (100,0,0,None),(108,-.5,28,"S"),(113,0,0,None)):
    scene.frame_set(round(seconds*demo.FPS)+1)
    bpy.context.view_layer.update()
    check_ammeter(scene,amps,framed=seconds in (26,35,61,113))
    assert sum(not o.hide_render for o in guides+extra)==count,(seconds,"field density")
    assert abs(switch.rotation_euler.y-math.radians(-43)*(1-abs(amps/.5)))<1e-6
    labels = [o for o in scene.objects if "switch_on" in o and not o.hide_render]
    assert len(labels)==1 and labels[0]["switch_on"] == (amps!=0)
    poles = [o for o in scene.objects if "pole" in o and not o.hide_render]
    assert len(poles)==(0 if left_pole is None else 2),(seconds,"poles")
    if left_pole:
        assert next(o for o in poles if o["side"]=="left")["pole"]==left_pole
    for needle,center in zip(needles,demo.COMPASS_CENTERS):
        assert abs(needle.rotation_euler.z-demo.needle_angle_at(seconds,center))<1e-6
        if seconds>=26:
            assert (needle.matrix_world.translation-Vector(demo.compass_center_at(seconds,center))).length<1e-6
            assert abs(needle.parent.scale.x-demo.COMPASS_SCALE)<1e-6
    if seconds>=32:
        assert abs(cell.rotation_euler.z-math.pi)<1e-6
    if seconds in (26,35):
        sign = 1 if amps>0 else -1
        for name,_,electron_direction in with_ammeter():
            if name.startswith("Far"):
                continue
            site = next(o for o in scene.objects if o.name=="Coil case field site | "+name)
            arrow = next(o for o in scene.objects if o.parent==site and "chevron" in o.name)
            points = [arrow.matrix_world@Vector(p.co[:3]) for p in arrow.data.splines[0].points]
            radial = points[1]-site.matrix_world.translation
            expected = -amps*Vector(electron_direction).cross(radial)
            actual = points[1]-(points[0]+points[2])/2
            assert actual.dot(expected)>0,(seconds,name,"branch circulation")
        roots = [o for o in scene.objects if o.name.startswith("Moving field arrow") and o.name.endswith("| "+str(sign))]
        assert len(roots)==4
        for root in roots:
            direction = root.rotation_quaternion@Vector((1,0,0))
            _,coil_field = demo.circuit_fields(tuple(root.location),1,demo.TURNS,demo.RADIUS)
            assert direction.dot(Vector(coil_field)*sign)>0,(seconds,"field arrow circulation")
    if seconds in (35,113):
        for obj in scene.objects:
            if obj.name.startswith("Battery body"):
                for corner in obj.bound_box:
                    uv = world_to_camera_view(scene,scene.camera,obj.matrix_world@Vector(corner))
                    assert .02<uv.x<.98 and .02<uv.y<.98,(seconds,"battery clipped",tuple(uv))
        label = labels[0]
        for corner in label.bound_box:
            uv = world_to_camera_view(scene,scene.camera,label.matrix_world@Vector(corner))
            assert .01<uv.x<.99 and .01<uv.y<.99,(seconds,"switch-state label clipped",tuple(uv))
    if seconds==108:
        assert all(c.location.z>1.2 for c in clips)
    if seconds==113:
        assert all(.035<c.location.z<.6 for c in clips), "Release should remain visibly in progress"
scene.frame_set(round(113.5*demo.FPS)+1)
assert all(abs(c.location.z-.035)<1e-6 for c in clips)
scene.frame_set(round(8*demo.FPS)+1)
assert all(o.hide_render is False for o in lower+upper), "Paired local coil fields should be visible after switch ON"
assert sum(not o.hide_render for o in current_arrows)>0, "Conventional-current arrows should be visible"
scene.frame_set(round(18*demo.FPS)+1)
assert scene.camera.location.x>6, "Camera should orbit right for a 3D field view"
scene.frame_set(round(86*demo.FPS)+1)
assert all(abs(r.rotation_euler.y)<1e-6 for r in regions)
assert all(abs(o.rotation_euler.y)<1e-6 for o in scene.objects if o.get("magnetic_direction"))
scene.frame_set(round(81*demo.FPS)+1)
assert any(abs(o.rotation_euler.y)>.5 for o in scene.objects if o.get("magnetic_direction"))
assert all(r.animation_data is None for r in regions), "Region positions and shapes stay fixed"
assert all(o.hide_render for o in scene.objects if o.name.startswith("Coil field direction caption"))
assert all("current creates" not in text.lower() for text in SUMMARY)
assert len([o for o in scene.objects if o.get("application_highlight")])==3
image = next(i for i in bpy.data.images if "electromagnetism-applications" in i.name)
assert image.packed_file
assert demo.DURATION-demo.APPLICATIONS_START == demo.APPLICATIONS_DURATION == 11
for frame in range(round(demo.APPLICATIONS_START*demo.FPS)+1,scene.frame_end+1):
    scene.frame_set(frame)
    visible = [o for o in scene.objects if o.get("application_highlight") and not o.hide_render]
    assert len(visible)==3, (frame,"All magnetic components must remain highlighted")
assert len([o for o in scene.objects if o.get("nail_region_outline")])==1
for seconds in (26,35,61,93):
    scene.frame_set(round(seconds*demo.FPS)+1)
    labels = [o.data.body for o in scene.objects if o.type=="FONT" and not o.hide_render]
    assert demo.INSIDE_FIELD_LABEL in labels and demo.OUTSIDE_FIELD_LABEL in labels
    assert demo.compass_center_at(93,demo.COMPASS_CENTERS[0])[0] < demo.COMPASS_CENTERS[0][0]
scene.frame_set(1)
for seconds in (26,35,61,93):
    left = demo.needle_angle_at(seconds,demo.COMPASS_CENTERS[0])
    right = demo.needle_angle_at(seconds,demo.COMPASS_CENTERS[1])
    assert abs(left-right)<1e-9, "Equal-distance compasses must show equal deflection"
print("PASS: preformed coil; paired local fields on every branch; conventional current; right-side 3D orbit; direct reversal; equal compasses; iron-core strength; stationary clips; summary and applications.")
