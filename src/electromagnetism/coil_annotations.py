"""Readable inside/outside direction captions for the coil comparisons."""
from . import coil_demo as demo, geometry as g
from .coil_keyframes import frames, CURRENT


def build(scene,mats,camera,group):
    annotations = []
    for sign in (1,-1):
        ink = mats["ink_cyan"]
        for inside,body,position,y,z in (
                (True,demo.INSIDE_FIELD_LABEL,(0,2.2,3.48),2.2,3.22),
                (False,demo.OUTSIDE_FIELD_LABEL,(0,-.1,1.12),-.1,.89)):
            name = "Coil field direction caption" if inside else "Coil outside field direction caption"
            label = g.face_camera(g.text(name,body,position,.23 if inside else .19,ink,group,align="CENTER"),camera)
            direction = -sign if inside else sign
            objects = [label]+g.arrow("Clear axial field direction" if inside else "Clear outside field direction",
                    (-.65*direction,y,z),(.65*direction,y,z),.065,ink,group)
            for obj in objects:
                obj["field_annotation"] = True
                shift = 0.
                annotations.append((sign,obj,obj.location.z,shift))
    for frame in frames(*CURRENT,(12,16),(44,50),(68,92),(99,103)):
        seconds = (frame-1)/demo.FPS
        reading_board = False
        for sign,obj,base_z,shift in annotations:
            obj.location.z = base_z+shift*demo.core_fraction(seconds)
            obj.keyframe_insert("location",frame=frame)
            # The clip close-up focuses on attraction and release; the field
            # guides remain visible without additional comparison captions.
            obj.hide_render = obj.hide_viewport = (demo.field_fraction(seconds)<.999
                or demo.current_at(seconds)*sign<=.001 or reading_board or seconds>=100)
            obj.keyframe_insert("hide_render",frame=frame)
            obj.keyframe_insert("hide_viewport",frame=frame)
