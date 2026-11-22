import os
import time
from pathlib import Path
from typing import List, Dict

from .video_ingestion import get_video_properties, generate_thumbnail
from .action_perception import infer_actions
from .config import USE_EPIC_MODEL
from .highlight_generator import generate_highlights_video
from .schemas import VideoResult

def process_video(input_path: str, output_json_path: str, output_mp4_path: str) -> VideoResult:
    """End‑to‑end processing of a video.

    - Extract metadata and thumbnail.
    - Run action inference.
    - Select highlight segments (~15% duration).
    - Generate highlights MP4.
    - Write JSON evaluation file.
    """
    start_total = time.time()
    # Ensure output directories exist
    os.makedirs(Path(output_json_path).parent, exist_ok=True)
    os.makedirs(Path(output_mp4_path).parent, exist_ok=True)

    # 1. Video properties
    t0 = time.time()
    props = get_video_properties(input_path)
    duration = props["duration"]
    t1 = time.time()

    # 2. Optional thumbnail (saved for UI)
    thumb_path = Path(input_path).with_name(Path(input_path).stem + "_thumb.jpg")
    try:
        generate_thumbnail(input_path, timestamp=0.0, output_path=thumb_path)
    except Exception:
        thumb_path = None
    t2 = time.time()

    # 3. Action inference
    if USE_EPIC_MODEL:
        try:
            from .epic_adapter import infer_epic_actions
            detections = infer_epic_actions(input_path)
        except Exception as e:
            # Report error and abort – do not silently fallback
            raise RuntimeError(f"EPIC model inference failed: {e}")
    else:
        detections = infer_actions(input_path)
    t3 = time.time()

    # 4. Highlight selection (target ~15% of original duration)
    highlights = select_highlights(detections, video_duration=duration, target_ratio=0.15)
    t4 = time.time()

    # 5. Generate highlights video (skip if no highlights)
    if highlights:
        generate_highlights_video(input_path, highlights, output_mp4_path)
    else:
        # No highlights to generate; mark as skipped in metrics
        output_mp4_path = None
    t5 = time.time()

    # 6. Build full result (internal analytics)
    result = VideoResult(
        video_id=Path(input_path).stem,
        label="action_summary",
        actions=[
            {
                "verb": d["verb"],
                "noun": d["noun"],
                "start": d["start"],
                "end": d["end"],
                "confidence": d["confidence"],
                "label": d["label"],
            }
            for d in detections
        ],
        highlights=[
            {
                "start": h["start"],
                "end": h["end"],
                "importance": h["importance"],
            }
            for h in highlights
        ],
        thumbnail=str(thumb_path) if thumb_path else None,
    )

    # 7. Create Samsung‑compliant JSON (full schema)
    submission = {
        "team_id": "T07",  # placeholder – should be consistent across runs
        "video_id": result.video_id,
        "duration_sec": duration,
        "label": {
            "name": result.label,
            "score": 1.0,  # placeholder confidence – R3D‑18 does not provide video‑level score
        },
        "actions": [
            {
                "segment": [a["start"], a["end"]],
                "verb": a["verb"],
                "noun": a["noun"],
                "score": a["confidence"] if "confidence" in a else 1.0,
            }
            for a in result.actions
        ],
        "highlights": [
            {
                "segment": [h["start"], h["end"]]
            }
            for h in result.highlights
        ],
    }

    # 8. Validate JSON if validator available; fallback simple schema check
    validator_path = Path(__file__).parent.parent / "validate.py"
    if validator_path.is_file():
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("validate", str(validator_path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "validate"):
                mod.validate(submission)
        except Exception as e:
            raise RuntimeError(f"JSON validation failed: {e}")
    else:
        # Simple fallback: ensure required keys exist and types are correct
        required_keys = {"video_id", "label", "actions", "highlights"}
        if not required_keys.issubset(submission.keys()):
            raise RuntimeError("Submission JSON missing required fields")
        if not isinstance(submission["actions"], list) or not isinstance(submission["highlights"], list):
            raise RuntimeError("'actions' and 'highlights' must be lists")

    # 9. Write submission JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        import json as _json
        _json.dump(submission, f, indent=2)
    t6 = time.time()

    # 10. Write metrics file (optional, not part of submission)
    metrics = {
        "ingestion_time_s": t1 - t0,
        "thumbnail_time_s": t2 - t1,
        "inference_time_s": t3 - t2,
        "selection_time_s": t4 - t3,
        "stitching_time_s": t5 - t4,
        "total_time_s": t6 - start_total,
    }
    metrics_path = Path(output_json_path).with_name(Path(output_json_path).stem + "_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        _json.dump(metrics, f, indent=2)

    return result
import time
from pathlib import Path
from typing import List, Dict

from .video_ingestion import get_video_properties, generate_thumbnail
from .action_perception import infer_actions
from .config import USE_EPIC_MODEL
from .highlight_generator import generate_highlights_video
from .schemas import VideoResult

def process_video(input_path: str, output_json_path: str, output_mp4_path: str) -> VideoResult:
    """End‑to‑end processing of a video.

    - Extract metadata and thumbnail.
    - Run action inference.
    - Select highlight segments (~15% duration).
    - Generate highlights MP4.
    - Write JSON evaluation file.
    """
    start_total = time.time()
    # Ensure output directories exist
    os.makedirs(Path(output_json_path).parent, exist_ok=True)
    os.makedirs(Path(output_mp4_path).parent, exist_ok=True)

    # 1. Video properties
    t0 = time.time()
    props = get_video_properties(input_path)
    duration = props["duration"]
    t1 = time.time()

    # 2. Optional thumbnail (saved for UI)
    thumb_path = Path(input_path).with_name(Path(input_path).stem + "_thumb.jpg")
    try:
        generate_thumbnail(input_path, timestamp=0.0, output_path=thumb_path)
    except Exception:
        thumb_path = None
    t2 = time.time()

    # 3. Action inference
    if USE_EPIC_MODEL:
        try:
            from .epic_adapter import infer_epic_actions
            detections = infer_epic_actions(input_path)
        except Exception as e:
            # Report error and abort – do not silently fallback
            raise RuntimeError(f"EPIC model inference failed: {e}")
    else:
        detections = infer_actions(input_path)
    t3 = time.time()

    # 4. Highlight selection (target ~15% of original duration)
    highlights = select_highlights(detections, video_duration=duration, target_ratio=0.15)
    t4 = time.time()

    # 5. Generate highlights video (skip if no highlights)
    if highlights:
        generate_highlights_video(input_path, highlights, output_mp4_path)
    else:
        # No highlights to generate; mark as skipped in metrics
        output_mp4_path = None
    t5 = time.time()

    # 6. Build full result (internal analytics)
    result = VideoResult(
        video_id=Path(input_path).stem,
        label="action_summary",
        actions=[
            {
                "verb": d["verb"],
                "noun": d["noun"],
                "start": d["start"],
                "end": d["end"],
                "confidence": d["confidence"],
                "label": d["label"],
            }
            for d in detections
        ],
        highlights=[
            {
                "start": h["start"],
                "end": h["end"],
                "importance": h["importance"],
            }
            for h in highlights
        ],
        thumbnail=str(thumb_path) if thumb_path else None,
    )

    # 7. Create Samsung‑compliant JSON (full schema)
    submission = {
        "team_id": "T07",  # placeholder – should be consistent across runs
        "video_id": result.video_id,
        "duration_sec": duration,
        "label": {
            "name": result.label,
            "score": 1.0,  # placeholder confidence – R3D‑18 does not provide video‑level score
        },
        "actions": [
            {
                "segment": [a["start"], a["end"]],
                "verb": a["verb"],
                "noun": a["noun"],
                "score": a["confidence"] if "confidence" in a else 1.0,
            }
            for a in result.actions
        ],
        "highlights": [
            {
                "segment": [h["start"], h["end"]]
            }
            for h in result.highlights
        ],
    }

    # 8. Validate JSON using internal validator (backend/validator.py)
    from .validator import validate_submission
    try:
        validate_submission(submission)
    except Exception as e:
        raise RuntimeError(f"JSON validation failed: {e}")

    # 9. Write submission JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        import json as _json
        _json.dump(submission, f, indent=2)
    t6 = time.time()

    # 10. Write metrics file (optional, not part of submission)
    metrics = {
        "ingestion_time_s": t1 - t0,
        "thumbnail_time_s": t2 - t1,
        "inference_time_s": t3 - t2,
        "selection_time_s": t4 - t3,
        "stitching_time_s": t5 - t4,
        "total_time_s": t6 - start_total,
    }
    metrics_path = Path(output_json_path).with_name(Path(output_json_path).stem + "_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        _json.dump(metrics, f, indent=2)

    return result
