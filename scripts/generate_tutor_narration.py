"""Author cached tutor speech; student playback is entirely offline.

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
    provenance['speaker'] = lesson['speaker']
    for index, section in enumerate(lesson["segments"]):
        clip = section.get("clip", index)
        path = output / f"narration_{clip:02}.mp3"
        spoken = section.get('speech_text', section['text'])
        digest = hashlib.sha256((spoken + lesson["description"]).encode()).hexdigest()
        cached = provenance['clips'].get(path.name, {})
        if path.exists() and cached.get('script_sha256') == digest and cached.get('voice') == lesson['speaker']:
            print(f"KEEP {path.name}", flush=True)
            continue
        for attempt in range(3):
            try:
                voice = edge_tts.Communicate(spoken, lesson["speaker"], boundary="WordBoundary")
                await voice.save(str(path), str(path.with_suffix(".words.jsonl")))
                break
            except Exception:
                if attempt == 2:
                    raise
                await asyncio.sleep(2*(attempt+1))
        provenance["clips"][path.name] = {"script_sha256": digest, "voice": lesson["speaker"]}
        provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
        print(f"READY {path.name}: {section.get('id',index)}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", default="docs/first-case-narration.json")
    asyncio.run(main(parser.parse_args().script))
