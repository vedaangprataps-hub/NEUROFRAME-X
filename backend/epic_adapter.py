# EPIC-KITCHENS TSM inference adapter
"""Adapter for loading a pretrained TSM model (verb+noun) from EPIC-KITCHENS-100
and running inference on a video.

The model expects RGB input of shape (B, C, T, H, W) where T is the number of
segments (clips). For simplicity we reuse the same sliding‑window logic as
`infer_actions` – a fixed clip length (default 2 s) and stride (0.5 s).

The checkpoint `weights/epic/tsm_rgb.ckpt` is a pure ``state_dict`` saved by the
official repository. The model architecture lives in the cloned repo
`epic_epic_model/src/models/tsm.py`.  We add the repository to ``sys.path`` at
runtime so the import works without packaging.

The function ``infer_epic_actions`` returns a list of detection dicts with the
exact same keys as the R3D‑18 implementation (verb, noun, start, end,
confidence, label).  It also filters out predictions that are not present in the
Samsung vocabulary (see ``student_kit/supported_classes.json``).
"""

import os
import sys
import json
import cv2
import torch
import numpy as np
from pathlib import Path
from typing import List, Dict

# Ensure the EPIC model code is importable
_EPIC_ROOT = Path(__file__).parent.parent / "epic_epic_model"
if str(_EPIC_ROOT) not in sys.path:
    sys.path.append(str(_EPIC_ROOT))

from src.models.tsm import TSM  # type: ignore

# ---------------------------------------------------------------------------
# Helper: load EPIC verb / noun class mappings
# ---------------------------------------------------------------------------
_VERB_CSV_URL = (
    "https://raw.githubusercontent.com/epic-kitchens/epic-kitchens-100-annotations/master/EPIC_100_verb_classes.csv"
)
_NOUN_CSV_URL = (
    "https://raw.githubusercontent.com/epic-kitchens/epic-kitchens-100-annotations/master/EPIC_100_noun_classes.csv"
)

def _download_csv(url: str, dest: Path) -> None:
    if dest.is_file():
        return
    # Use PowerShell Invoke-WebRequest – it works on Windows without extra tools
    cmd = f"powershell -Command \"Invoke-WebRequest -Uri '{url}' -OutFile '{dest}'\""
    from .utils import run_shell  # placeholder – we will implement a tiny helper below
    run_shell(cmd)

def _load_class_map(csv_path: Path) -> Dict[int, str]:
    mapping: Dict[int, str] = {}
    with csv_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("id"):
                continue
            parts = line.split(",")
            if len(parts) < 2:
                continue
            idx = int(parts[0])
            key = parts[1]
            mapping[idx] = key
    return mapping

# Download CSVs lazily
_DATA_DIR = Path(__file__).parent / "epic_data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_verb_csv = _DATA_DIR / "EPIC_100_verb_classes.csv"
_noun_csv = _DATA_DIR / "EPIC_100_noun_classes.csv"
_download_csv(_VERB_CSV_URL, _verb_csv)
_download_csv(_NOUN_CSV_URL, _noun_csv)

_VERB_MAP = _load_class_map(_verb_csv)
_NOUN_MAP = _load_class_map(_noun_csv)

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
_CHECKPOINT = Path(__file__).parent.parent / "weights" / "epic" / "tsm_rgb.ckpt"

def _load_model() -> TSM:
    # EPIC uses (num_verbs, num_nouns) tuple for multi‑task heads
    num_verbs = max(_VERB_MAP.keys()) + 1
    num_nouns = max(_NOUN_MAP.keys()) + 1
    model = TSM(num_class=(num_verbs, num_nouns), num_segments=8, modality="RGB")
    state_dict = torch.load(str(_CHECKPOINT), map_location="cpu")
    # The checkpoint may contain a 'state_dict' wrapper – handle both cases
    if "state_dict" in state_dict:
        state_dict = state_dict["state_dict"]
    # Strip possible "module." prefixes (from DataParallel)
    state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}
    # Verify multi‑task heads exist
    verb_head = any("fc_verb" in k for k in state_dict.keys())
    noun_head = any("fc_noun" in k for k in state_dict.keys())
    if not (verb_head and noun_head):
        raise RuntimeError(
            "Loaded EPIC checkpoint does not contain separate verb and noun heads. "
            "Cannot perform verb‑noun inference with this checkpoint."
        )
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    return model
    # EPIC uses (num_verbs, num_nouns) tuple for multi‑task heads
    num_verbs = max(_VERB_MAP.keys()) + 1
    num_nouns = max(_NOUN_MAP.keys()) + 1
    model = TSM(num_class=(num_verbs, num_nouns), num_segments=8, modality="RGB")
    state_dict = torch.load(str(_CHECKPOINT), map_location="cpu")
    # The checkpoint may contain a 'state_dict' wrapper – handle both cases
    if "state_dict" in state_dict:
        state_dict = state_dict["state_dict"]
    # Strip possible "module." prefixes (from DataParallel)
    state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    return model

_MODEL = None

def _get_model() -> TSM:
    global _MODEL
    if _MODEL is None:
        _MODEL = _load_model()
    return _MODEL

# ---------------------------------------------------------------------------
# Inference utilities (frame extraction, transform)
# ---------------------------------------------------------------------------
from torchvision import transforms

_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def _extract_clip_frames(cap: cv2.VideoCapture, start_frame: int, num_frames: int) -> List[np.ndarray]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frames: List[np.ndarray] = []
    for _ in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return frames

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def infer_epic_actions(video_path: str, clip_len_sec: float = 2.0, stride_sec: float = 0.5) -> List[Dict]:
    """Run EPIC‑KITCHENS TSM inference.

    Returns a list of detections with the same schema as ``action_perception.
    infer_actions`` so the rest of the pipeline can remain unchanged.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        raise RuntimeError("Unable to read FPS from video")
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    clip_len_frames = int(clip_len_sec * fps)
    stride_frames = max(int(stride_sec * fps), 1)
    detections: List[Dict] = []

    # Load Samsung vocab for filtering
    kit_root = Path(__file__).parent.parent / "student_kit"
    vocab_path = kit_root / "supported_classes.json"
    if vocab_path.is_file():
        vocab_data = json.load(vocab_path.open())
        allowed_verbs = set(vocab_data.get("verbs", []))
        allowed_nouns = set(vocab_data.get("nouns", []))
    else:
        allowed_verbs = set()
        allowed_nouns = set()

    model = _get_model()

    for start in range(0, total_frames - clip_len_frames + 1, stride_frames):
        frames = _extract_clip_frames(cap, start, clip_len_frames)
        if len(frames) < clip_len_frames:
            break
        # Transform each frame
        tensor_frames = torch.stack([_transform(Image.fromarray(f)) for f in frames])  # (T, C, H, W)
        # TSM expects (B, C, T, H, W)
        tensor_frames = tensor_frames.permute(1, 0, 2, 3).unsqueeze(0)
        with torch.no_grad():
            verb_logits, noun_logits = model(tensor_frames)
            verb_probs = torch.nn.functional.softmax(verb_logits, dim=1).squeeze(0)
            noun_probs = torch.nn.functional.softmax(noun_logits, dim=1).squeeze(0)
            verb_idx = verb_probs.argmax().item()
            noun_idx = noun_probs.argmax().item()
            verb = _VERB_MAP.get(verb_idx, "")
            noun = _NOUN_MAP.get(noun_idx, "")
            confidence = (verb_probs[verb_idx] * noun_probs[noun_idx]).item()
            # Apply Samsung vocab filter – skip if not allowed or empty
            if not verb or not noun:
                continue
            if allowed_verbs and verb not in allowed_verbs:
                continue
            if allowed_nouns and noun not in allowed_nouns:
                continue
        start_sec = start / fps
        end_sec = (start + clip_len_frames) / fps
        detections.append({
            "verb": verb,
            "noun": noun,
            "start": round(start_sec, 3),
            "end": round(end_sec, 3),
            "confidence": round(confidence, 4),
            "label": f"{verb} {noun}".strip(),
        })
    cap.release()

    # Merge adjacent detections of same verb‑noun pair (same logic as R3D‑18)
    merged: List[Dict] = []
    for det in detections:
        if not merged:
            merged.append(det)
            continue
        prev = merged[-1]
        if (
            det["verb"] == prev["verb"]
            and det["noun"] == prev["noun"]
            and det["start"] - prev["end"] <= 0.3
        ):
            prev["end"] = det["end"]
            prev["confidence"] = max(prev["confidence"], det["confidence"])
        else:
            merged.append(det)
    return merged
