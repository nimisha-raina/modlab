"""Author cached tutor speech; student playback is entirely offline.

Uses edge-tts, an LGPL-3.0 client for Microsoft's Edge speech service. Only the
public lesson script is sent. Voice output is not an Apache-licensed model.
"""
import asyncio
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg
import numpy as np

from prepare_coil_bilingual import normalize, save_wave

ROOT = Path(__file__).resolve().parents[1]


def delivery_settings(lesson):
    return {
        "rate": lesson.get("rate", "+0%"),
        "volume": lesson.get("volume", "+0%"),
        "pitch": lesson.get("pitch", "+0Hz"),
        "sentence_leveling": bool(lesson.get("sentence_leveling", False)),
        "sentence_pause_seconds": float(lesson.get("sentence_pause_seconds", 0.20)),
    }


async def synthesize(text, path, words_path, lesson):
    settings = delivery_settings(lesson)
    for attempt in range(3):
        try:
            voice = edge_tts.Communicate(
                text, lesson["speaker"], boundary="WordBoundary",
                rate=settings["rate"], volume=settings["volume"],
                pitch=settings["pitch"],
            )
            await voice.save(str(path), str(words_path))
            return
        except Exception:
            if attempt == 2:
                raise
            await asyncio.sleep(2 * (attempt + 1))


async def synthesize_levelled(spoken, destination, lesson, clip):
    """Match sentence loudness, clean joins, then encode the clip only once."""
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", spoken) if part.strip()]
    cache = destination.parent / ".sentence-cache" / f"narration_{clip:02}"
    cache.mkdir(parents=True, exist_ok=True)
    rate = 44100
    pause = np.zeros(round(delivery_settings(lesson)["sentence_pause_seconds"] * rate), dtype="<i2")
    pieces = []
    combined_words = []
    cursor = 0
    for number, sentence in enumerate(sentences):
        raw = cache / f"{number:02}.mp3"
        words_path = cache / f"{number:02}.words.jsonl"
        await synthesize(sentence, raw, words_path, lesson)
        samples = normalize(raw, cache / f"{number:02}.wav", rate)
        words = [json.loads(line) for line in words_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        first_offset = words[0]["offset"] if words else 0
        base_offset = round(cursor / rate * 10_000_000)
        for word in words:
            word["offset"] = base_offset + max(0, word["offset"] - first_offset)
            combined_words.append(word)
        pieces.append(samples)
        cursor += len(samples)
        if number + 1 < len(sentences):
            pieces.append(pause)
            cursor += len(pause)
    master = cache / "levelled.wav"
    save_wave(master, np.concatenate(pieces), rate)
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-i", str(master),
        "-codec:a", "libmp3lame", "-b:a", "192k", str(destination),
    ], check=True)
    destination.with_suffix(".words.jsonl").write_text(
        "".join(json.dumps(word, ensure_ascii=False) + "\n" for word in combined_words),
        encoding="utf-8",
    )


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
    settings = delivery_settings(lesson)
    provenance['delivery'] = settings
    for index, section in enumerate(lesson["segments"]):
        clip = section.get("clip", index)
        path = output / f"narration_{clip:02}.mp3"
        spoken = section.get('speech_text', section['text'])
        digest = hashlib.sha256((spoken + lesson["description"]).encode()).hexdigest()
        delivery_digest = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()
        cached = provenance['clips'].get(path.name, {})
        if (path.exists() and cached.get('script_sha256') == digest
                and cached.get('voice') == lesson['speaker']
                and cached.get('delivery_sha256') == delivery_digest):
            print(f"KEEP {path.name}", flush=True)
            continue
        if settings["sentence_leveling"]:
            await synthesize_levelled(spoken, path, lesson, clip)
        else:
            await synthesize(spoken, path, path.with_suffix(".words.jsonl"), lesson)
        provenance["clips"][path.name] = {
            "script_sha256": digest,
            "voice": lesson["speaker"],
            "delivery_sha256": delivery_digest,
        }
        provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
        print(f"READY {path.name}: {section.get('id',index)}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", default="docs/first-case-narration.json")
    asyncio.run(main(parser.parse_args().script))
