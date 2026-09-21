"""Update packed language scenes from the saved storyboard without rebuilding it."""
from pathlib import Path
import sys
import argparse
import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from electromagnetism.coil_narration import attach
PART=ROOT/'output/parts/02_coil_reversal/bilingual'

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--languages',nargs='+',choices=('english','hinglish'),default=['english','hinglish'])
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
for language in args.languages:
    bpy.ops.wm.open_mainfile(filepath=str(PART/'coil_bilingual_source.blend'))
    scene=bpy.context.scene
    timing=attach(scene,PART/f'audio_{language}')
    scene['narration_language']=language
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(PART/f'coil_{language}.blend'))
    print(f'PACKED_LANGUAGE_SCENE={language}: {timing["duration"]:.2f}s',flush=True)
