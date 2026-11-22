import cv2
from pathlib import Path
from typing import Tuple, List, Dict
import json

def get_video_properties(video_path: str) -> Dict[str, any]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps else 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration": duration,
        "width": width,
        "height": height,
    }

def sample_frames(video_path: str, interval_sec: float = 1.0) -> List[Tuple[int, any]]:
    """Return a list of (frame_index, frame_image) sampled every interval_sec seconds."""
    props = get_video_properties(video_path)
    fps = props["fps"]
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_idx = 0
    interval_frames = int(fps * interval_sec)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % interval_frames == 0:
            frames.append((frame_idx, frame))
        frame_idx += 1
    cap.release()
    return frames

def generate_thumbnail(video_path: str, timestamp: float = 0.0, output_path: str = None) -> str:
    """Extract a single frame at `timestamp` seconds and save as JPEG. Returns the path."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps * timestamp))
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError("Failed to capture thumbnail frame")
    if output_path is None:
        output_path = Path(video_path).with_suffix("_thumb.jpg")
    cv2.imwrite(str(output_path), frame)
    return str(output_path)
