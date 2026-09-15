"""Check the exported video's frames, narration alignment and question silence.

Run with .venv-media/bin/python after rendering. Compare the actual decoded
audio with each prepared WAV; timeline metadata alone cannot detect a silent
export, missing section, or shifted soundtrack.
"""
import json
from pathlib import Path
import subprocess

import av
import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RATE = 16000


def decode_audio(path):
    raw = subprocess.check_output([
        imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
        "-i", str(path), "-vn", "-ar", str(SAMPLE_RATE), "-ac", "1",
        "-f", "s16le", "-",
    ])
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768


def main():
    timing = json.loads((ROOT / "output/audio/narration-timing.json").read_text())
    video_path = ROOT / "output/video/electromagnetism.mp4"
    with av.open(video_path) as video:
        stream = video.streams.video[0]
        assert stream.frames == timing["frames"], "Rendered frame count differs from the speech timeline."
        assert float(stream.average_rate) == timing["fps"]
        assert video.streams.audio, "The video has no audio track."
    mixed = decode_audio(video_path)
    assert abs(len(mixed) / SAMPLE_RATE - timing["duration"]) < .1
    results = []
    for index, segment in enumerate(timing["segments"]):
        reference = decode_audio(ROOT / segment["audio"])
        # Blender rounds sound-strip placement to the nearest whole frame.
        expected = round((segment["target_start"] + .2) * timing["fps"]) / timing["fps"]
        start = max(0, round((expected - .15) * SAMPLE_RATE))
        end = min(len(mixed), round((expected + .15) * SAMPLE_RATE) + len(reference))
        # Decimation keeps the correlation small while retaining 0.5 ms timing.
        a, b = reference[::8], mixed[start:end:8]
        similarity = np.correlate(b, a, mode="valid")
        offset = int(np.argmax(similarity))
        match = b[offset:offset + len(a)]
        score = float(similarity[offset] / max(np.linalg.norm(a) * np.linalg.norm(match), 1e-12))
        actual = (start + offset * 8) / SAMPLE_RATE
        error = abs(actual - expected)
        assert score > .8, f"Section {index+1} is missing or differs from its prepared speech (correlation {score:.3f})."
        assert error < 1 / timing["fps"] + .01, f"Section {index+1} is shifted by {error:.3f}s."
        results.append({"section": index + 1, "alignment_error_seconds": round(error, 4),
                        "audio_correlation": round(score, 4)})
    questions = json.loads((ROOT / "student-lesson/content/questions.json").read_text())
    for question in questions:
        pause = timing["segments"][question["after_section"]-1]["target_end"] - .3
        around_pause = mixed[round((pause-.05)*SAMPLE_RATE):round((pause+.05)*SAMPLE_RATE)]
        assert float(np.sqrt(np.mean(around_pause**2))) < .003, "A question interrupts audible speech."
    report = {"frames": timing["frames"], "duration": timing["duration"],
              "sections": results, "question_pauses": "All fall in silence after narration."}
    (ROOT / "output/audio/video-verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print("PASS: the exported video contains every narration section at the correct time.")


if __name__ == "__main__":
    main()
