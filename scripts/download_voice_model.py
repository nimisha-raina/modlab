"""Download pinned voice assets using the project's Hugging Face connection.

Run with .venv-media/bin/python after approving `hf auth login`. The local
inference environment uses an older Transformers release and stays offline.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / ".cache/huggingface"))

from huggingface_hub import snapshot_download

snapshot_download(
    "ai4bharat/indic-parler-tts",
    revision="7b527af5ee8ed1f9a28d80b19703ed9bb8ba10ca",
    local_dir=ROOT / ".cache/models/indic-parler-tts", token=True,
)
snapshot_download(
    "google/flan-t5-large",
    revision="0613663d0d48ea86ba8cb3d7a44f0f65dc596a2a",
    allow_patterns=["tokenizer*", "spiece.model", "special_tokens_map.json", "config.json"],
    local_dir=ROOT / ".cache/models/flan-t5-large-tokenizer", token=False,
)
print("Voice assets are ready for offline generation.")
