"""Render cached 720p frames and encode the complete narrated fixed-view movie."""
import argparse
import hashlib
import json
import math
import os
import shutil
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from render_coil_review import fingerprint

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT/"output/parts/02_coil_reversal"
CACHE = PART/"fixed_view_frames"
REPORT = PART/"fixed-view-render.json"


def render(stills, fps=6, reuse_prefix=False):
    import bpy
    previous, previous_order = None,None
    if reuse_prefix:
        # The only allowed revision is to the clips and their board headings.
        # Check every earlier frame before reusing any cached picture.
        previous = json.loads((PART/"fixed-view-render-v1.json").read_text())
        original = PART/"coil_fixed_view_review_v1.blend"
        assert hashlib.sha256(original.read_bytes()).hexdigest()==previous["source_sha256"]
        assert previous["fps"]==fps
        current = bpy.data.filepath
        bpy.ops.wm.open_mainfile(filepath=str(original))
        previous_order = [o.name for o in bpy.context.scene.objects]
        bpy.ops.wm.open_mainfile(filepath=current)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x,scene.render.resolution_y = 1280,720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.use_sequencer = False
    scene.eevee.taa_render_samples = 8
    timing = json.loads(scene["narration_timing"])
    from electromagnetism.timing import map_time
    if stills:
        for source in stills:
            scene.frame_set(round(map_time(source,timing)*24)+1)
            scene.render.filepath = str(PART/f"fixed_{source:05.1f}s.png")
            bpy.ops.render.render(write_still=True)
        return
    CACHE.mkdir(exist_ok=True)
    source_digest = hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
    seen,sequence = set(),[]
    for index in range(round(timing["duration"]*fps)):
        scene.frame_set(round(index*24/fps)+1)
        bpy.context.view_layer.update()
        digest = fingerprint(scene,source_digest)
        path = CACHE/(digest+".png")
        if previous and index < math.ceil(map_time(99,timing)*fps):
            before = fingerprint(scene,previous["source_sha256"],previous_order)
            assert before+".png"==previous["sequence"][index],f"Earlier picture changed at {index/fps}s; full render required"
            if not path.is_file():
                shutil.copy2(CACHE/previous["sequence"][index],path)
        if not path.is_file():
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
        seen.add(digest)
        sequence.append(path.name)
        if index%(fps*5) == 0:
            print(f"FIXED_PROGRESS={index/fps:.1f}s UNIQUE={len(seen)}",flush=True)
    report = dict(duration=timing["duration"],fps=fps,width=1280,height=720,
                  unique_states=len(seen),sequence=sequence,source_sha256=source_digest)
    if previous:
        report["verified_prefix_reuse"] = dict(source_sha256=previous["source_sha256"],
            frames=math.ceil(map_time(99,timing)*fps),reason="Only clip placement and later board headings changed; all earlier state fingerprints matched.")
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print("FIXED_RENDER_COMPLETE",flush=True)


def encode():
    import subprocess
    import imageio_ffmpeg
    from PIL import Image
    report = json.loads(REPORT.read_text())
    target = PART/"coil_fixed_view_narrated_720p.mp4"
    temporary = target.with_name("encoding_"+target.name)
    command = [imageio_ffmpeg.get_ffmpeg_exe(),"-v","error","-y","-f","rawvideo","-pix_fmt","rgb24",
        "-s","1280x720","-r",str(report["fps"]),"-i","-","-i",str(PART/"audio_fixed/narration.wav"),
        "-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
        "-movflags","+faststart",str(temporary)]
    process = subprocess.Popen(command,stdin=subprocess.PIPE)
    previous,data = None,None
    for name in report["sequence"]:
        if name != previous:
            with Image.open(CACHE/name) as picture:
                data = picture.convert("RGB").tobytes()
            previous = name
        process.stdin.write(data)
    process.stdin.close()
    if process.wait():
        raise RuntimeError("Encoding failed")
    try:
        os.replace(temporary,target)
    except PermissionError:
        # A media player may have the earlier review open on Windows.
        target = target.with_name("coil_fixed_view_narrated_720p_v2.mp4")
        os.replace(temporary,target)
    timing = json.loads((PART/"audio_fixed/narration-timing.json").read_text())
    timing.update(fps=report["fps"],frames=len(report["sequence"]),video_file=target.name)
    (PART/"audio_fixed/video-timing.json").write_text(json.dumps(timing,indent=2)+"\n")
    print(f"NARRATED_VIDEO={target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stills",type=float,nargs="*",default=[])
    parser.add_argument("--encode",action="store_true")
    parser.add_argument("--fps",type=int,choices=(6,12),default=6)
    parser.add_argument("--reuse-prefix",action="store_true",help="Verify and reuse the v1 review before the clip-only revision at source second 99")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else ([] if "bpy" in sys.modules else sys.argv[1:]))
    encode() if args.encode else render(args.stills,args.fps,args.reuse_prefix)
