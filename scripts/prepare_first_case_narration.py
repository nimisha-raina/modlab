"""Fit narration to the approved first-case movie without changing speech speed."""
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import wave

import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / "output/parts/01_compass_current"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def run(*args):
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], check=True)


def main():
    # Restore included recordings for offline authoring in a fresh checkout.
    from restore_assets import restore
    restore()
    lesson = json.loads((ROOT / "docs/first-case-narration.json").read_text(encoding="utf-8"))
    audio_dir = ROOT / lesson.get("audio_directory", "output/parts/01_compass_current/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)
    included = ROOT / lesson.get("audio_assets", "assets/first-case-narration")
    if included.exists():
        for source in included.iterdir():
            if source.is_file() and not (audio_dir / source.name).exists():
                shutil.copy2(source, audio_dir / source.name)
    questions = json.loads((ROOT / "student-lesson/content/questions.json").read_text(encoding="utf-8"))
    quiz_sections = {q["after_section"] - 1 for q in questions}
    provenance = json.loads((audio_dir / "provenance.json").read_text(encoding="utf-8"))
    rate = 44100
    track = np.zeros(round(lesson["duration"] * rate), dtype=np.int16)
    oversized = []
    for index, segment in enumerate(lesson["segments"]):
        source = audio_dir / f"narration_{segment.get('clip', index):02}.mp3"
        digest = hashlib.sha256((segment["text"] + lesson["description"]).encode()).hexdigest()
        if provenance["clips"].get(source.name, {}).get("script_sha256") != digest:
            raise SystemExit(f"Regenerate stale or unverified narration: {source.name}")
        target = source.with_suffix(".wav")
        run("-i", source, "-af",
            "silenceremove=start_periods=1:start_duration=0.06:start_threshold=-55dB:start_silence=0.03,areverse,"
            "silenceremove=start_periods=1:start_duration=0.06:start_threshold=-55dB:start_silence=0.15,areverse,"
            "highpass=f=60,"
            "loudnorm=I=-18:TP=-2:LRA=7", "-ar", rate, "-ac", 1, "-c:a", "pcm_s16le", target)
        with wave.open(str(target), "rb") as audio:
            samples = np.frombuffer(audio.readframes(audio.getnframes()), dtype="<i2").astype(np.float64)
        # Raised-cosine fades join speech to silence without an abrupt waveform edge.
        for length, edge in ((round(.02 * rate), "in"), (round(.10 * rate), "out")):
            length = min(length, len(samples))
            envelope = (1 - np.cos(np.linspace(0, np.pi, length))) / 2
            if edge == "in":
                samples[:length] *= envelope
            else:
                samples[-length:] *= envelope[::-1]
        samples = np.rint(np.clip(samples, -32768, 32767)).astype("<i2")
        with wave.open(str(target), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(rate)
            audio.writeframes(samples.tobytes())
        duration = len(samples) / rate
        start = round((segment["start"] + lesson.get("lead_seconds", .2)) * lesson["fps"]) / lesson["fps"]
        # Leave extra quiet time before the two H5P pauses at end minus .3s.
        tail = .45 if index in quiz_sections else .12
        available = segment["end"] - tail - start
        print(f"{index:02}: {duration:.3f}s / {available:.3f}s available", flush=True)
        if duration > available:
            oversized.append(index)
        offset = round(start * rate)
        if offset + len(samples) <= len(track):
            track[offset:offset + len(samples)] = samples
        segment.update(audio=str(target.relative_to(ROOT)).replace("\\", "/"),
                       speech_seconds=round(duration, 3), target_start=segment["start"],
                       target_end=segment["end"], speech_start=start)
    if oversized:
        raise SystemExit(f"Shorten and regenerate narration segments {oversized}; speech must not be accelerated.")
    lesson["frames"] = round(lesson["duration"] * lesson["fps"])
    timing = audio_dir / "narration-timing.json"
    timing.write_text(json.dumps(lesson, indent=2) + "\n", encoding="utf-8")
    mixed = audio_dir / "narration.wav"
    with wave.open(str(mixed), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(track.tobytes())
    movie = PART / "opening_and_compass_narrated_720p.mp4"
    approved = ROOT / lesson.get("video_source", "output/parts/01_compass_current/opening_and_compass_review_720p.mp4")
    if not approved.exists():
        approved = ROOT / "student-lesson/dist/assets/electromagnetism.mp4"
        import av
        with av.open(approved) as video:
            if abs(float(video.duration / av.time_base) - lesson["duration"]) > .1:
                raise SystemExit("Build/render the revised tutor sequence before preparing its soundtrack.")
    run("-i", approved, "-i", mixed,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
        "-b:a", "160k", "-t", lesson["duration"], "-movflags", "+faststart", movie)
    content = ROOT / "student-lesson/content"
    shutil.copy2(timing, content / "narration-timing.json")
    captions = [[s["start"], s["end"], "Electricity makes magnetism", s["text"]]
                for s in lesson["segments"]]
    (content / "captions.json").write_text(json.dumps(captions, indent=2) + "\n", encoding="utf-8")
    assets = ROOT / "student-lesson/dist/assets"
    shutil.copy2(movie, assets / "electromagnetism.mp4")
    run("-ss", 1, "-i", movie, "-frames:v", 1, assets / "poster.jpg")
    print(f"Prepared {lesson['duration']}-second narrated movie and lesson assets.")


if __name__ == "__main__":
    main()
