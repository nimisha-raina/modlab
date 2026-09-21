"""Create localized source and narrated, packed Blender scenes for Case 1."""
import argparse
import json
from pathlib import Path
import sys
import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from electromagnetism import apparatus_highlights
from electromagnetism.narration import curves
from electromagnetism.timing import map_time

PART=ROOT/'output/parts/01_compass_current/bilingual'
SCENES=('01 - Electricity makes magnetism','02 - Compass and current')


def localized_plane(obj,item):
    """Shaped Devanagari on a portable image plane at the original text anchor."""
    bounds=obj.bound_box
    x0,x1=min(v[0] for v in bounds),max(v[0] for v in bounds)
    y0,y1=min(v[1] for v in bounds),max(v[1] for v in bounds)
    max_width=obj.get('localized_width',x1-x0)
    height=obj.get('localized_height',(y1-y0)*1.25)
    if obj.parent and obj.parent.type=='CAMERA' and not obj.get('localized_height'):
        height=max(height,obj.data.size*1.1)
        max_width*=1.2
    scale=min(max_width/item['width'],height/item['height'])
    width,height=item['width']*scale,item['height']*scale
    # Preserve alignment and the original black panel's usable width.
    left=x0 if obj.data.align_x=='LEFT' else x1-width if obj.data.align_x=='RIGHT' else (x0+x1-width)/2
    bottom=(y0+y1-height)/2
    mesh=bpy.data.meshes.new(obj.name+' | shaped letters')
    mesh.from_pydata([(left,bottom,0),(left+width,bottom,0),(left+width,bottom+height,0),(left,bottom+height,0)],[],[(0,1,2,3)])
    uv=mesh.uv_layers.new()
    for loop,coord in zip(uv.data,((0,0),(1,0),(1,1),(0,1))):loop.uv=coord
    plane=bpy.data.objects.new(obj.name+' | Hindi',mesh)
    for collection in obj.users_collection:collection.objects.link(plane)
    plane.parent=obj.parent
    plane.matrix_parent_inverse=obj.matrix_parent_inverse.copy()
    plane.matrix_basis=obj.matrix_basis.copy()
    plane.hide_render=obj.hide_render
    plane.hide_viewport=obj.hide_viewport
    if obj.animation_data and obj.animation_data.action:
        plane.animation_data_create()
        plane.animation_data.action=obj.animation_data.action
        plane.animation_data.action_slot=obj.animation_data.action_slot
    for constraint in obj.constraints:
        new=plane.constraints.new(constraint.type)
        for prop in constraint.bl_rna.properties:
            if not prop.is_readonly and prop.identifier not in ('type','rna_type'):
                try:setattr(new,prop.identifier,getattr(constraint,prop.identifier))
                except (AttributeError,TypeError):pass
    material=obj.data.materials[0].copy()
    material.name='Hindi lettering | '+obj.name
    tree=material.node_tree
    output=next(n for n in tree.nodes if n.type=='OUTPUT_MATERIAL')
    original=output.inputs['Surface'].links[0].from_socket
    picture=tree.nodes.new('ShaderNodeTexImage')
    picture.image=bpy.data.images.load(str(PART/'text'/item['file']),check_existing=True)
    picture.image.pack()
    picture.extension='CLIP'
    clear=tree.nodes.new('ShaderNodeBsdfTransparent')
    mix=tree.nodes.new('ShaderNodeMixShader')
    # Binary coverage keeps small shaped letters solid at review sample counts.
    coverage=tree.nodes.new('ShaderNodeMath')
    coverage.operation='GREATER_THAN'
    coverage.inputs[1].default_value=.45
    tree.links.new(picture.outputs['Alpha'],coverage.inputs[0])
    tree.links.new(coverage.outputs[0],mix.inputs[0])
    tree.links.new(clear.outputs[0],mix.inputs[1])
    tree.links.new(original,mix.inputs[2])
    tree.links.new(mix.outputs[0],output.inputs['Surface'])
    mesh.materials.append(material)
    for key in obj.keys():plane[key]=obj[key]
    plane['lesson_text']=item['text']
    plane['source_text']=obj.data.body
    bpy.data.objects.remove(obj,do_unlink=True)
    return plane


def retime(scene,timing,offset):
    actions=set()
    for obj in scene.objects:
        blocks=[obj,obj.data,getattr(obj.data,'shape_keys',None)]
        blocks += [m.node_tree for m in getattr(obj.data,'materials',[]) if m and m.node_tree]
        for block in blocks:
            if block and getattr(block,'animation_data',None) and block.animation_data.action:
                actions.add(block.animation_data.action)
    origin=map_time(offset,timing)
    for action in actions:
        for curve in curves(action):
            for key in curve.keyframe_points:
                for point in (key.co,key.handle_left,key.handle_right):
                    point.x=(map_time((point.x-1)/24+offset,timing)-origin)*24+1
            curve.update()
    for marker in scene.timeline_markers:
        marker.frame=round((map_time((marker.frame-1)/24+offset,timing)-origin)*24)+1
    for name in ('switch_on_frame','switch_off_frame'):
        if name in scene:
            scene[name]=round((map_time((scene[name]-1)/24+offset,timing)-origin)*24)+1
    scene.frame_end=round((map_time(offset+(48 if offset==0 else 38),timing)-origin)*24)
    scene.frame_set(1)


def fit_translated_panels(scene):
    """Keep compact backplates fitted to the actual shaped Hindi lettering."""
    bpy.context.view_layer.update()
    labels=[obj for obj in scene.objects if obj.get('source_text')]
    for plate in scene.objects:
        if plate.name.startswith('Terminal connection label plate'):
            bodies={'FROM BATTERY (-)'} if plate.location.x<0 else {'TOWARDS BATTERY (+)'}
        elif plate.name.startswith('Switch state card'):
            bodies={'CIRCUIT STATUS','SWITCH  OPEN','SWITCH  CLOSED'}
        elif plate.name.startswith('Flow comparison plate'):
            bodies={'Electron flow   -  >>>  +','Conventional current   -  <<<  +'}
        else:continue
        selected=[obj for obj in labels if obj['source_text'] in bodies]
        if not selected:continue
        points=[(obj.location.x*8+v[0],obj.location.y*8+v[1]) for obj in selected for v in obj.bound_box]
        left,right=min(p[0] for p in points),max(p[0] for p in points)
        bottom,top=min(p[1] for p in points),max(p[1] for p in points)
        depth=8/7.95
        width,height=(right-left)*depth+.16,(top-bottom)*depth+.10
        vertices=plate.data.vertices
        old_width=max(v.co.x for v in vertices)-min(v.co.x for v in vertices)
        old_height=max(v.co.y for v in vertices)-min(v.co.y for v in vertices)
        for vertex in vertices:
            vertex.co.x*=width/old_width
            vertex.co.y*=height/old_height
        plate.location.x=(left+right)*depth/16
        plate.location.y=(bottom+top)*depth/16
        plate['text_width']=(right-left)*depth/8


def main(language,delivery_only=False):
    bpy.ops.wm.open_mainfile(filepath=str(PART/(f'case_one_{language}_source.blend' if delivery_only else 'case_one_source.blend')))
    folder=PART/f'audio_{language}'
    timing=json.loads((folder/'narration-timing.json').read_text(encoding='utf-8'))
    labels=json.loads((PART/'text/labels.json').read_text(encoding='utf-8'))
    intro=bpy.data.scenes[SCENES[0]]
    bpy.context.window.scene=intro
    if not delivery_only:apparatus_highlights.build(intro,json.loads((folder/'apparatus-cues.json').read_text()))
    localized=0
    for name in SCENES:
        scene=bpy.data.scenes[name]
        bpy.context.window.scene=scene
        scene.frame_set(1)
        bpy.context.view_layer.update()
        for obj in list(scene.objects):
            if obj.type!='FONT':continue
            item=labels[obj.data.body][language]
            if item['text']!=obj.data.body:
                localized_plane(obj,item)
                localized+=1
        if language=='hinglish' and not delivery_only:fit_translated_panels(scene)
        scene['language']=language
    if not delivery_only:bpy.ops.wm.save_as_mainfile(filepath=str(PART/f'case_one_{language}_source.blend'))
    for name,offset in zip(SCENES,(0,48)):retime(bpy.data.scenes[name],timing,offset)
    assembly=bpy.data.scenes['00 - Opening and compass']
    editor=assembly.sequence_editor_create()
    for strip in list(editor.strips):editor.strips.remove(strip)
    cursor=1
    for name in SCENES:
        scene=bpy.data.scenes[name]
        strip=editor.strips.new_scene(name,scene,channel=1,frame_start=cursor)
        strip.frame_final_duration=scene.frame_end
        cursor+=scene.frame_end
    sound=editor.strips.new_sound('Indian tutor | '+timing['speaker'],str(folder/'narration.wav'),channel=2,frame_start=1)
    sound.sound.pack()
    assembly.frame_end=timing['frames']
    assembly.render.fps=24
    assembly.render.use_sequencer=True
    assembly['narration_timing']=json.dumps(timing,ensure_ascii=False)
    assembly['language']=language
    assembly['narrator']=timing['speaker']
    bpy.context.window.scene=assembly
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(PART/f'case_one_{language}.blend'))
    print(f'LOCALIZED_SCENE_READY={language} labels={localized}',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=('english','hinglish'),required=True)
    parser.add_argument('--delivery-only',action='store_true',help='Repack the narrated edit without changing the rendered source')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    main(args.language,args.delivery_only)
