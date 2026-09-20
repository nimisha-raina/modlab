"""Author cached male Indian-English speech; student playback is entirely offline.

Uses edge-tts, an LGPL-3.0 client for Microsoft's Edge speech service. Only the
public lesson script is sent. Voice output is not an Apache-licensed model.
"""
import asyncio
import argparse
import hashlib
import json
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]


async def main(script="docs/first-case-narration.json"):
    lesson = json.loads((ROOT / script).read_text(encoding="utf-8"))
    output = ROOT / lesson["audio_directory"]
    output.mkdir(parents=True, exist_ok=True)
    provenance_path = output / "provenance.json"
    provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {
        "speaker": lesson["speaker"], "service": "Microsoft Edge speech service",
        "client": "edge-tts 7.2.8", "client_license": "LGPL-3.0",
        "client_source": "https://github.com/rany2/edge-tts", "clips": {},
    }
    for index, section in enumerate(lesson["segments"]):
        clip = section.get("clip", index)
        path = output / f"narration_{clip:02}.mp3"
        digest = hashlib.sha256((section["text"] + lesson["description"]).encode()).hexdigest()
        if path.exists() and provenance["clips"].get(path.name, {}).get("script_sha256") == digest:
            print(f"KEEP {path.name}", flush=True)
            continue
        voice = edge_tts.Communicate(section["text"], lesson["speaker"], boundary="WordBoundary")
        await voice.save(str(path), str(path.with_suffix(".words.jsonl")))
        provenance["clips"][path.name] = {"script_sha256": digest, "voice": lesson["speaker"]}
        provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
        print(f"READY {path.name}: {section['text']}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", default="docs/first-case-narration.json")
    asyncio.run(main(parser.parse_args().script))
