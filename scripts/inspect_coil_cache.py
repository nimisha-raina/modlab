"""Read-only report of scene state differences across one current-arrow cycle."""
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from render_coil_review import fingerprint
scene=bpy.context.scene
def state(t):
    scene.frame_set(round(t*24)+1)
    bpy.context.view_layer.update()
    result={}
    for obj in scene.objects:
        if obj.hide_render or obj.type not in ('MESH','FONT','CURVE'):continue
        result[obj.name]=(tuple(round(x,6) for row in obj.matrix_world for x in row),
                          getattr(getattr(obj.data,'shape_keys',None),'eval_time',None))
    return result,fingerprint(scene,'inspect')
a,ha=state(18.25)
b,hb=state(20.25)
print('CYCLE_HASH_EQUAL',ha==hb,flush=True)
print('CHANGED_OBJECTS',[(k,a.get(k),b.get(k)) for k in a.keys()|b.keys() if a.get(k)!=b.get(k)],flush=True)
