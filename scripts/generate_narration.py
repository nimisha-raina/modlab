"""Generate reusable narration clips with AI4Bharat's official public demo.

Only the public lesson script and voice description are sent. No student data,
account information, or credentials are used. Existing clips are preserved.
"""
import json
import argparse
import hashlib
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://ai4bharat-indic-parler-tts.hf.space"
API = ORIGIN + "/gradio_api"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", type=Path, default=ROOT / "docs/narration.json")
    parser.add_argument("--output", type=Path, default=ROOT / "output/audio")
    args = parser.parse_args()
    lesson = json.loads(args.script.read_text())
    if lesson["model"] != "ai4bharat/indic-parler-tts":
        raise SystemExit("Use generate_tutor_narration.py for the current Microsoft Edge voice.")
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    provenance_path = output / "provenance.json"
    provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {
        "model": lesson["model"], "license": "Apache-2.0", "speaker": lesson["speaker"],
        "model_card": "https://huggingface.co/ai4bharat/indic-parler-tts", "clips": {},
    }
    for index, segment in enumerate(lesson["segments"]):
        destination = output / f"narration_{segment.get('clip', index):02}.mp3"
        digest = hashlib.sha256((segment["text"]+lesson["description"]).encode()).hexdigest()
        previous = provenance.get("clips", {}).get(destination.name, {})
        if destination.exists() and destination.stat().st_size > 1000 and previous.get("script_sha256", digest) == digest:
            print(f"KEEP {destination.name}", flush=True)
            continue
        data = json.dumps({"data": [segment["text"], lesson["description"]]}).encode()
        request = urllib.request.Request(API + "/call/generate_finetuned", data=data,
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=60) as response:
            event_id = json.load(response)["event_id"]
        result = None
        with urllib.request.urlopen(API + "/call/generate_finetuned/" + event_id, timeout=180) as response:
            event = ""
            for raw in response:
                line = raw.decode().strip()
                if line.startswith("event: "):
                    event = line[7:]
                elif line.startswith("data: ") and event == "error":
                    raise RuntimeError(line)
                elif line.startswith("data: ") and event == "complete":
                    result = json.loads(line[6:])[0]
        if not result or not result["path"].startswith("/tmp/gradio/"):
            raise RuntimeError("The voice service did not return an audio artifact.")
        # Gradio 5's demo response repeats its API prefix in `url`. Use the
        # returned artifact path with the demo's declared file endpoint.
        with urllib.request.urlopen(API + "/file=" + result["path"], timeout=60) as response:
            destination.write_bytes(response.read())
        print(f"READY {destination.name}: {segment['text']}", flush=True)
        provenance.setdefault("clips", {})[destination.name] = {
            "method": "official public demo",
            "script_sha256": digest,
            "service": "https://huggingface.co/spaces/ai4bharat/indic-parler-tts",
        }
        provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")


if __name__ == "__main__":
    main()
