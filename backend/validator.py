"""Internal Samsung Student Kit JSON validator.

Based on `TEAM_README.md` and the example JSON files in the
student_kit folder.  The validator raises ``ValueError`` with a
human‑readable message when any constraint is violated.
"""
import json
from pathlib import Path
from typing import List, Dict, Any

# Load the vocabulary once at import time.
_KIT_ROOT = Path(__file__).parents[1] / "student_kit"
_SUPPORTED = json.loads((_KIT_ROOT / "supported_classes.json").read_text())
_LABELS: List[str] = _SUPPORTED["labels"]
_VERBS: List[str] = _SUPPORTED["verbs"]
_NOUNS: List[str] = _SUPPORTED["nouns"]

MANIFEST = {}
_manifest_path = _KIT_ROOT / "manifest.csv"
if _manifest_path.is_file():
    for line in _manifest_path.read_text().splitlines()[1:]:  # skip header
        video_id, dur, _ = line.split(",")
        MANIFEST[video_id] = float(dur)

def _float_range(v: Any, name: str, low: float, high: float) -> float:
    try:
        fv = float(v)
    except Exception:
        raise ValueError(f"{name} must be a number, got {v!r}")
    if not (low <= fv <= high):
        raise ValueError(f"{name}={fv} out of allowed range [{low}, {high}]")
    return fv

def validate_submission(data: Dict[str, Any]) -> None:
    """Validate a single JSON submission.

    The function raises ``ValueError`` on the first violation.
    """
    # ----- top‑level fields -----
    required_top = {"team_id", "video_id", "duration_sec", "label", "actions", "highlights"}
    missing = required_top - data.keys()
    if missing:
        raise ValueError(f"Missing top‑level fields: {sorted(missing)}")

    # team_id – non‑empty string
    if not isinstance(data["team_id"], str) or not data["team_id"].strip():
        raise ValueError("team_id must be a non‑empty string")

    video_id = data["video_id"]
    if not isinstance(video_id, str) or not video_id:
        raise ValueError("video_id must be a non‑empty string")

    # duration_sec – positive, within ±0.5 s of manifest if present
    dur = _float_range(data["duration_sec"], "duration_sec", 0.0, 1e6)
    if video_id in MANIFEST and abs(dur - MANIFEST[video_id]) > 0.5:
        raise ValueError(f"duration_sec {dur} differs >0.5 s from manifest value {MANIFEST[video_id]}")

    # label object
    label = data["label"]
    if not isinstance(label, dict):
        raise ValueError("label must be an object")
    if "name" not in label or "score" not in label:
        raise ValueError("label must contain 'name' and 'score'")
    if label["name"] not in _LABELS:
        raise ValueError(f"label.name '{label['name']}' not in supported labels")
    _float_range(label["score"], "label.score", 0.0, 1.0)

    # ----- actions -----
    actions = data["actions"]
    if not isinstance(actions, list):
        raise ValueError("actions must be a list")
    for i, a in enumerate(actions):
        if not isinstance(a, dict):
            raise ValueError(f"action[{i}] must be an object")
        for k in ("segment", "verb", "noun", "score"):
            if k not in a:
                raise ValueError(f"action[{i}] missing field '{k}'")
        # segment must be list of two numbers, start < end, within video duration (+0.5)
        seg = a["segment"]
        if not (isinstance(seg, list) and len(seg) == 2):
            raise ValueError(f"action[{i}].segment must be a two‑element list")
        start = _float_range(seg[0], f"action[{i}].segment[0]", 0.0, dur + 0.5)
        end = _float_range(seg[1], f"action[{i}].segment[1]", start, dur + 0.5)
        # verb / noun must belong to vocab
        if a["verb"] not in _VERBS:
            raise ValueError(f"action[{i}].verb '{a['verb']}' not in supported verbs")
        if a["noun"] not in _NOUNS:
            raise ValueError(f"action[{i}].noun '{a['noun']}' not in supported nouns")
        _float_range(a["score"], f"action[{i}].score", 0.0, 1.0)

    # ----- highlights -----
    highlights = data["highlights"]
    if not isinstance(highlights, list):
        raise ValueError("highlights must be a list")  # Empty highlights allowed
    total_hl = 0.0
    prev_end = -1.0
    for i, h in enumerate(highlights):
        if not isinstance(h, dict) or "segment" not in h:
            raise ValueError(f"highlights[{i}] must be an object with 'segment'")
        seg = h["segment"]
        if not (isinstance(seg, list) and len(seg) == 2):
            raise ValueError(f"highlights[{i}].segment must be a two‑element list")
        start = _float_range(seg[0], f"highlights[{i}].segment[0]", 0.0, dur + 0.5)
        end = _float_range(seg[1], f"highlights[{i}].segment[1]", start, dur + 0.5)
        # chronological order & no overlap
        if start < prev_end:
            raise ValueError(f"highlights[{i}] starts before previous end (overlap)")
        prev_end = end
        length = end - start
        if length < 4.0:
            # allowed but will be ignored during scoring – we treat as warning only
            pass
        total_hl += length
    # budget: total highlight duration <= 15% of video duration
    if total_hl > 0.15 * dur:
        raise ValueError(f"total highlight duration {total_hl:.2f}s exceeds 15% budget of {0.15 * dur:.2f}s")

    # All checks passed
    return None
