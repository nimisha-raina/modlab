"""Render a complete silent visual review, reusing identical scene states.

Run inside Blender to render; run with the media Python and --encode to make
the MP4. A scene-state fingerprint avoids rendering stationary holds twice.
The editable source keeps its continuous 24-fps animation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from electromagnetism import coil_demo as demo
PART = ROOT/"output/parts/02_coil_reversal"
FRAMES = PART/"extended_review_frames"


def fingerprint(scene, source_digest):
    state = [(source_digest,scene.render.resolution_x,scene.render.resolution_y)]
    materials = set()
    for obj in scene.objects:
        if obj.hide_render or obj.type not in ("MESH","CURVE","FONT"):
            continue
        state.append((obj.name,tuple(round(v,6) for row in obj.matrix_world for v in row)))
        keys = getattr(obj.data,"shape_keys",None)
        if keys:
            state.append((obj.name,"keys",round(keys.eval_time,5),tuple(round(k.value,6) for k in keys.key_blocks)))
        for mat in obj.data.materials:
            if mat:
                materials.add(mat)
    for mat in sorted(materials,key=lambda m:m.name):
        if mat.use_nodes:
            node = mat.node_tree.nodes.get("Guide opacity")
            if node:
                state.append((mat.name,round(node.inputs[0].default_value,6)))
    state.append(("camera",tuple(round(v,6) for row in scene.camera.matrix_world for v in row)))
    return hashlib.sha256(repr(state).encode()).hexdigest()


def render(fps,width,stills=()):
    import bpy
    scene = bpy.data.scenes[demo.SCENE_NAME]
    bpy.context.window.scene = scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x,scene.render.resolution_y = width,round(width*9/16)
    scene.render.resolution_percentage = 100
    scene.render.use_sequencer = False
    scene.render.image_settings.file_format = "PNG"
    scene.eevee.taa_render_samples = 8
    FRAMES.mkdir(parents=True,exist_ok=True)
    for seconds in stills:
        if not 0<=seconds<demo.DURATION:
            raise ValueError("Still time must be inside the lesson")
        scene.render.resolution_x,scene.render.resolution_y = 1280,720
        scene.frame_set(round(seconds*demo.FPS)+1)
        scene.render.filepath = str(PART/f"review_{seconds:05.1f}s.png")
        bpy.ops.render.render(write_still=True)
    scene.render.resolution_x,scene.render.resolution_y = width,round(width*9/16)
    with Path(bpy.data.filepath).open("rb") as source:
        source_digest = hashlib.file_digest(source,"sha256").hexdigest()
    seen,sequence = {},[]
    for index in range(demo.DURATION*fps):
        scene.frame_set(round(index*demo.FPS/fps)+1)
        bpy.context.view_layer.update()
        digest = fingerprint(scene,source_digest)
        path = FRAMES/(digest+".png")
        if digest not in seen:
            if not path.is_file():
                scene.render.filepath = str(path)
                bpy.ops.render.render(write_still=True)
            seen[digest] = path.name
        sequence.append(path.name)
        if index % (fps*5) == 0:
            print(f"REVIEW_PROGRESS={index/fps:.1f}s UNIQUE_STATES={len(seen)}",flush=True)
    report = {"duration":demo.DURATION,"fps":fps,"width":width,"height":round(width*9/16),
              "unique_states":len(seen),"sequence":sequence}
    (PART/"extended-render.json").write_text(json.dumps(report,indent=2)+"\n")
    print("EXTENDED_REVIEW_RENDERED",flush=True)


def encode():
    import imageio_ffmpeg
    import subprocess
    from PIL import Image
    report = json.loads((PART/"extended-render.json").read_text())
    target = PART/f"coil_reversal_draft_{report['fps']}fps.mp4"
    command = [imageio_ffmpeg.get_ffmpeg_exe(),"-hide_banner","-loglevel","error","-y",
               "-f","rawvideo","-pix_fmt","rgb24","-s",f"{report['width']}x{report['height']}",
               "-r",str(report["fps"]),"-i","-","-an","-c:v","libx264","-crf","18",
               "-pix_fmt","yuv420p","-movflags","+faststart",str(target)]
    process = subprocess.Popen(command,stdin=subprocess.PIPE)
    previous,data = None,None
    for name in report["sequence"]:
        if name != previous:
            with Image.open(FRAMES/name) as picture:
                data = picture.convert("RGB").tobytes()
            previous = name
        process.stdin.write(data)
    process.stdin.close()
    if process.wait():
        raise RuntimeError("Video encoder failed")
    print(f"EXTENDED_REVIEW_VIDEO={target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encode",action="store_true")
    parser.add_argument("--fps",type=int,choices=(4,6,12),default=6)
    parser.add_argument("--width",type=int,choices=(640,1280),default=640)
    parser.add_argument("--stills",type=float,nargs="*",default=(),help="Also render selected 720p stills before the movie frames")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:])
    encode() if args.encode else render(args.fps,args.width,args.stills)
