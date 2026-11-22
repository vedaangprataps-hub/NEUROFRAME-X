from typing import List, Dict
import heapq
from typing import List, Dict, Tuple

def select_highlights(detections: List[Dict], video_duration: float, target_ratio: float = 0.15) -> List[Dict]:
    """Select highlight segments using a budgeted knapsack with diversity scoring.

    Args:
        detections: List of action detections (must contain 'start', 'end', 'confidence').
        video_duration: Total length of the video in seconds.
        target_ratio: Desired total highlight duration as a fraction of video length.

    Returns:
        List of highlight dicts with 'start', 'end', 'importance' (0‑1).
    """
    target_seconds = video_duration * target_ratio
    if target_seconds <= 0:
        return []

    # Compute a base score = confidence. Apply diversity penalty based on verb‑noun reuse.
    verb_counts: Dict[Tuple[str, str], int] = {}
    scored_segments: List[Tuple[float, Dict]] = []
    for det in detections:
        verb = det.get('verb', '').strip()
        noun = det.get('noun', '').strip()
        key = (verb, noun)
        verb_counts[key] = verb_counts.get(key, 0) + 1
        # Diversity factor: first occurrence 1.0, second 0.5, third 0.25, etc.
        diversity = 1.0 / (2 ** (verb_counts[key] - 1))
        base_conf = det.get('confidence', 0.0)
        score = base_conf * diversity
        scored_segments.append((score, det))

    # Sort by score descending.
    scored_segments.sort(key=lambda x: x[0], reverse=True)

    selected: List[Dict] = []
    total_selected = 0.0
    for score, det in scored_segments:
        if total_selected >= target_seconds:
            break
        seg_start = det['start']
        seg_end = det['end']
        seg_len = seg_end - seg_start
        if seg_len <= 0:
            continue
        # Overlap check with already selected (strict non‑overlap).
        overlap = any(not (seg_end <= s['start'] or seg_start >= s['end']) for s in selected)
        if overlap:
            continue
        # Do not exceed budget: skip segment if it would push total over target_seconds
        if total_selected + seg_len > target_seconds:
            continue
        selected.append({
            'start': seg_start,
            'end': seg_end,
            'importance': round(det.get('confidence', 0.0), 3),
        })
        total_selected += seg_len

    # If budget not reached, fill with lowest‑confidence non‑overlapping segments.
    if total_selected < target_seconds:
        for score, det in sorted(scored_segments, key=lambda x: x[0]):  # ascending
            # Ensure adding this segment does not exceed the budget
            seg_start = det['start']
            seg_end = det['end']
            seg_len = seg_end - seg_start
            if seg_len <= 0:
                continue
            # Overlap check
            if any(not (seg_end <= s['start'] or seg_start >= s['end']) for s in selected):
                continue
            # Budget check before adding
            if total_selected + seg_len > target_seconds:
                continue
            selected.append({
                'start': seg_start,
                'end': seg_end,
                'importance': round(det.get('confidence', 0.0), 3),
            })
            total_selected += seg_len
            if total_selected >= target_seconds:
                break
            seg_start = det['start']
            seg_end = det['end']
            seg_len = seg_end - seg_start
            if seg_len <= 0:
                continue
            if any(not (seg_end <= s['start'] or seg_start >= s['end']) for s in selected):
                continue
            selected.append({
                'start': seg_start,
                'end': seg_end,
                'importance': round(det.get('confidence', 0.0), 3),
            })
            total_selected += seg_len
            if total_selected >= target_seconds:
                break

    # Chronological order.
    selected.sort(key=lambda h: h['start'])
    return selected
