"""Normalize Case 2 speech and allocate natural, unhurried demonstration windows."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import wave
import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    lesson = json.loads((ROOT / "docs/coil-narration.json").read_text())
    folder = ROOT / lesson["audio_directory"]
    provenance = json.loads((folder / "provenance.json").read_text())
    rate, cursor, clips = 44100, 0., []
    for i, section in enumerate(lesson["segments"]):
        source = folder / f"narration_{i:02}.mp3"
        expected = hashlib.sha256((section["text"] + lesson["description"]).encode()).hexdigest()
        assert provenance["clips"][source.name]["script_sha256"] == expected
        target = source.with_suffix(".wav")
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-i", str(source),
            "-af", "silenceremove=start_periods=1:start_duration=0.06:start_threshold=-55dB:start_silence=0.03,areverse,"
            "silenceremove=start_periods=1:start_duration=0.06:start_threshold=-55dB:start_silence=0.15,areverse,"
            "highpass=f=60,loudnorm=I=-18:TP=-2:LRA=7", "-ar", str(rate), "-ac", "1", str(target)], check=True)
        with wave.open(str(target), "rb") as f:
            samples = np.frombuffer(f.readframes(f.getnframes()), dtype="<i2").astype(float)
        for count, beginning in ((round(.02*rate), True), (round(.10*rate), False)):
            envelope = (1-np.cos(np.linspace(0, np.pi, count)))/2
            if beginning:
                samples[:count] *= envelope
            else:
                samples[-count:] *= envelope[::-1]
        samples = np.rint(np.clip(samples, -32768, 32767)).astype("<i2")
        with wave.open(str(target), "wb") as f:
            f.setparams((1, 2, rate, 0, "NONE", "not compressed"))
            f.writeframes(samples.tobytes())
        duration = len(samples)/rate
        window = math.ceil(max(section["end"]-section["start"], duration+.8)*12)/12
        if i == len(lesson["segments"])-1:
            assert duration+.5 <= 11, "Shorten applications narration to fit the agreed 11-second display"
            window = 11.
        section.update(target_start=cursor, target_end=cursor+window, speech_start=cursor+.25,
                       speech_seconds=duration, audio=target.relative_to(ROOT).as_posix())
        clips.append((round((cursor+.25)*rate), samples))
        cursor += window
        print(f"{i:02}: speech={duration:.2f}s, window={window:.2f}s", flush=True)
    lesson.update(duration=cursor, frames=round(cursor*24), fps=24, source_duration=136)
    track = np.zeros(round(cursor*rate), dtype="<i2")
    for start, samples in clips:
        track[start:start+len(samples)] = samples
    with wave.open(str(folder / "narration.wav"), "wb") as f:
        f.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        f.writeframes(track.tobytes())
    (folder / "narration-timing.json").write_text(json.dumps(lesson, indent=2)+"\n", encoding="utf-8")
    print(f"COIL_NARRATION_READY={cursor:.2f}s")


if __name__ == "__main__":
    main()
