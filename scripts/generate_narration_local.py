"""Finish missing voice clips locally with the downloaded AI4Bharat model.

Run with .venv-voice/bin/python. Download the model and text tokenizer first
using the authenticated, newer hf CLI in .venv-media. Inference is offline;
this process neither reads the login credential nor calls a speech service.
"""
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
MODEL_REVISION = "7b527af5ee8ed1f9a28d80b19703ed9bb8ba10ca"


def main():
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HOME"] = str(ROOT / ".cache/voice-runtime")
    os.environ["MPLCONFIGDIR"] = str(ROOT / ".cache/matplotlib")
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    lesson = json.loads((ROOT / "docs/narration.json").read_text())
    output = ROOT / "output/audio"
    paths = [output / f"narration_{i:02}.mp3" for i in range(len(lesson["segments"]))]
    missing = [i for i, path in enumerate(paths) if not path.exists() or path.stat().st_size < 1000]
    if not missing:
        print("All narration clips already exist.")
        return

    import imageio_ffmpeg
    import numpy as np
    import soundfile as sf
    import torch
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer, set_seed

    torch.set_num_threads(6)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "mps" else torch.float32
    print(f"Loading the local model on {device}...", flush=True)
    model_path = ROOT / ".cache/models/indic-parler-tts"
    model = ParlerTTSForConditionalGeneration.from_pretrained(
        model_path, local_files_only=True, attn_implementation="eager",
        torch_dtype=dtype,
    ).to(device).eval()
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    description_tokenizer = AutoTokenizer.from_pretrained(
        ROOT / ".cache/models/flan-t5-large-tokenizer", local_files_only=True)
    description = description_tokenizer(lesson["description"], return_tensors="pt").to(device)
    sample_rate = model.audio_encoder.config.sampling_rate
    raw = output / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    provenance_path = output / "provenance.json"
    provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {
        "model": lesson["model"], "license": "Apache-2.0", "speaker": lesson["speaker"],
        "model_card": "https://huggingface.co/ai4bharat/indic-parler-tts",
        "clips": {f"narration_{i:02}.mp3": {"method": "official public demo"}
                  for i in range(len(lesson["segments"])) if i not in missing},
    }
    for index in missing:
        started = time.monotonic()
        text = lesson["segments"][index]["text"]
        print(f"Generating section {index + 1}: {text}", flush=True)
        prompt = tokenizer(text, return_tensors="pt").to(device)
        set_seed(42 + index)
        with torch.inference_mode():
            result = model.generate(
                input_ids=description.input_ids, attention_mask=description.attention_mask,
                prompt_input_ids=prompt.input_ids, prompt_attention_mask=prompt.attention_mask,
                do_sample=True, return_dict_in_generate=True, max_new_tokens=1400,
            )
        audio = result.sequences[0, :int(result.audios_length[0])].float().cpu().numpy().squeeze()
        if not np.isfinite(audio).all() or len(audio) < sample_rate:
            raise RuntimeError("The generated audio is empty or invalid.")
        # Match the public demo's peak-normalized export, retaining a raw WAV.
        audio = audio / max(float(np.abs(audio).max()), 1e-8) * .98
        wav = raw / f"narration_{index:02}.wav"
        sf.write(wav, audio, sample_rate, subtype="PCM_16")
        destination = output / f"narration_{index:02}.mp3"
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
                        "-y", "-i", str(wav), "-b:a", "320k", str(destination)], check=True)
        provenance.setdefault("clips", {})[destination.name] = {
            "method": "local inference", "model_revision": MODEL_REVISION,
            "device": device, "seed": 42 + index, "seconds": len(audio) / sample_rate,
        }
        provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
        print(f"READY {destination.name}: {len(audio)/sample_rate:.2f}s of audio; "
              f"generated in {time.monotonic()-started:.1f}s", flush=True)


if __name__ == "__main__":
    main()
