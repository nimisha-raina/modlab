"""Use measured speech alignment and word boundaries for the apparatus pointers."""
import json
from pathlib import Path
import subprocess
import wave
import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
lesson = json.loads((ROOT / "docs/first-case-narration.json").read_text())
folder = ROOT / lesson["audio_directory"]
source = folder / "narration_01.mp3"
raw = subprocess.check_output([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(source),
                               "-ar", "44100", "-ac", "1", "-f", "s16le", "-"])
raw = np.frombuffer(raw, dtype="<i2").astype(float)[::8]
with wave.open(str(source.with_suffix(".wav"))) as audio:
    prepared = np.frombuffer(audio.readframes(audio.getnframes()), dtype="<i2").astype(float)[::8]
# Locate the prepared opening inside the raw speech; gain changes do not shift it.
probe = prepared[:44100 // 8]
scores = np.correlate(raw[:len(probe) + 44100 // 16], probe, mode="valid")
trim = int(np.argmax(scores)) * 8 / 44100
start = round((3 + lesson["lead_seconds"]) * lesson["fps"]) / lesson["fps"]
words = [json.loads(line) for line in source.with_suffix(".words.jsonl").read_text().splitlines()]
terms = [("battery", "battery"), ("switch", "switch"), ("copper wire", "copper"),
         ("resistor", "resistor"), ("series ammeter", "series")]
cues = []
for name, keyword in terms:
    word = next(w for w in words if w["text"].lower() == keyword)
    cues.append({"component": name, "start": round(start + word["offset"] / 1e7 - trim - .05, 3)})
for index, cue in enumerate(cues):
    cue["end"] = cues[index + 1]["start"] if index + 1 < len(cues) else min(10, start + len(prepared)*8/44100 + .2)
target = folder / "apparatus-cues.json"
target.write_text(json.dumps(cues, indent=2) + "\n")
print(json.dumps({"prepared_start_trim":trim,"cues":cues}, indent=2))
