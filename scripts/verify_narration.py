"""Use local open-source speech recognition to flag missing/changed words.

Recognition is a useful check, not proof of accent quality. Inspect flagged
lines against the authored script before accepting the finished audio.
"""
import json
import argparse
import hashlib
from pathlib import Path
import re
from difflib import SequenceMatcher
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--script", type=Path, default=ROOT / "docs/narration.json")
parser.add_argument("--output", type=Path, default=ROOT / "output/audio")
parser.add_argument("--indices", nargs="+", type=int, help="Check only these zero-based sections; retain previous results.")
args = parser.parse_args()
model = WhisperModel("base.en", device="cpu", compute_type="int8", cpu_threads=4,
                     download_root=str(ROOT / ".cache/models"))
script = json.loads(args.script.read_text(encoding="utf-8"))
report = args.output / "transcript-check.json"
results = {item["clip"]: item for item in json.loads(report.read_text())} if report.exists() else {}
indices = args.indices if args.indices is not None else range(len(script["segments"]))
for index in indices:
    section = script["segments"][index]
    path = args.output / f"narration_{section.get('clip', index):02}.mp3"
    assert path.exists(), f"Narration section {index+1} is missing."
    chunks, info = model.transcribe(str(path), language="en", beam_size=5)
    actual = " ".join(chunk.text.strip() for chunk in chunks)
    words = lambda text: re.findall(r"[a-z]+", text.lower())
    similarity = SequenceMatcher(None, words(section["text"]), words(actual)).ratio()
    result = {"clip": index, "expected": section["text"], "recognised": actual,
              "similarity": round(similarity, 3), "duration": info.duration,
              "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    results[index] = result
    print(json.dumps(result), flush=True)
report.write_text(json.dumps([results[i] for i in sorted(results)], indent=2)+"\n")
