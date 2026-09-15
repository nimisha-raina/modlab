"""Normalize narration and calculate a relaxed, frame-aligned lesson timeline.

Run with .venv-media/bin/python. Speech is never sped up to fit the animation.
Blender stretches each matching scene section to fit its complete explanation.
"""
import json
import math
from pathlib import Path
import subprocess
import wave
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
FPS = 24
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
lesson = json.loads((ROOT / "docs/narration.json").read_text())
cursor = 0
for index, segment in enumerate(lesson["segments"]):
    source = ROOT / f"output/audio/narration_{index:02}.mp3"
    target = source.with_suffix(".wav")
    subprocess.run([ffmpeg,"-hide_banner","-loglevel","error","-y","-i",str(source),
        "-af", "silenceremove=start_periods=1:start_duration=0.06:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_duration=0.06:start_threshold=-45dB,areverse,loudnorm=I=-18:TP=-2:LRA=7",
        "-ar","44100","-ac","1","-c:a","pcm_s16le",str(target)], check=True)
    with wave.open(str(target)) as audio:
        duration = audio.getnframes()/audio.getframerate()
    frames = math.ceil(max(segment["end"]-segment["start"], duration+.8)*FPS)
    segment.update({"audio":str(target.relative_to(ROOT)),"speech_seconds":round(duration,3),
                    "target_start":cursor/FPS,"target_end":(cursor+frames)/FPS})
    cursor += frames
lesson.update({"fps":FPS,"duration":cursor/FPS,"frames":cursor})
(ROOT / "output/audio/narration-timing.json").write_text(json.dumps(lesson,indent=2)+"\n")
print(f"Narrated lesson: {cursor/FPS:.2f} seconds, {cursor} frames")
