# Action perception module for NEUROFRAME-X

"""Load the pretrained R3D-18 video classification model (trained on Kinetics-400) and run inference.

The module provides a single public function `infer_actions` that returns a list of detections with:
- verb, noun, start, end, confidence, label
"""

from PIL import Image

import torch
import numpy as np
from pathlib import Path
from typing import List, Dict
import torchvision.transforms as T
from torchvision.models.video import R3D_18_Weights
import json
import cv2

# Load weights and model
_weights = R3D_18_Weights.DEFAULT
_model = torch.hub.load('pytorch/vision', 'r3d_18', weights=_weights)
_model.eval()

# Retrieve full list of class labels from the weights metadata
_labels = _weights.meta["categories"]

# Transform pipeline for frames
_transform = T.Compose([
    T.Resize((112, 112)),
    T.ToTensor(),
    T.Normalize(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
])


def _extract_clip_frames(cap: cv2.VideoCapture, start_frame: int, num_frames: int, fps: float) -> List[np.ndarray]:
    """Extract a list of RGB frames from the video capture starting at `start_frame`."""
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frames = []
    for _ in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return frames


def infer_actions(video_path: str, clip_len_sec: float = 2.0, stride_sec: float = 0.5) -> List[Dict]:
    """Run action inference on a video.

    Returns a list of detections with keys:
    - verb, noun, start, end, confidence, label
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        raise RuntimeError("Unable to read FPS from video")
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    clip_len_frames = int(clip_len_sec * fps)
    stride_frames = max(int(stride_sec * fps), 1)
    raw_detections = []
    for start in range(0, total_frames - clip_len_frames + 1, stride_frames):
        frames = _extract_clip_frames(cap, start, clip_len_frames, fps)
        if len(frames) < clip_len_frames:
            break
        tensor_frames = torch.stack([_transform(Image.fromarray(frame)) for frame in frames])  # (T, C, H, W)
        tensor_frames = tensor_frames.permute(1, 0, 2, 3).unsqueeze(0)  # (1, C, T, H, W)
        with torch.no_grad():
            logits = _model(tensor_frames)
            probs = torch.nn.functional.softmax(logits, dim=1)
            top_prob, top_idx = probs.topk(1)
            prob = top_prob.item()
            idx = top_idx.item()
            label = _labels[idx] if idx < len(_labels) else f"class_{idx}"
            parts = label.split(" ", 1)
            verb = parts[0] if parts else ""
            noun = parts[1] if len(parts) > 1 else ""
            start_sec = start / fps
            end_sec = (start + clip_len_frames) / fps
            raw_detections.append({
                "verb": verb,
                "noun": noun,
                "start": round(start_sec, 3),
                "end": round(end_sec, 3),
                "confidence": round(prob, 4),
                "label": label,
            })
    cap.release()

    # Load supported vocabulary for validation (verbs, nouns)
    _supported_vocab_path = Path(__file__).parent.parent / "student_kit" / "supported_classes.json"
    if _supported_vocab_path.is_file():
        try:
            _supported_data = json.load(_supported_vocab_path)
            _supported_verbs = set(_supported_data.get("verbs", []))
            _supported_nouns = set(_supported_data.get("nouns", []))
        except Exception:
            _supported_verbs = set()
            _supported_nouns = set()
    else:
        _supported_verbs = set()
        _supported_nouns = set()

    # Post-processing: merge adjacent detections of same class within 0.3s gap
    merged = []
    for det in raw_detections:
        verb = det["verb"].strip()
        noun = det["noun"].strip()
        if not verb or not noun:
            continue
        if _supported_verbs and verb not in _supported_verbs:
            continue
        if _supported_nouns and noun not in _supported_nouns:
            continue
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
