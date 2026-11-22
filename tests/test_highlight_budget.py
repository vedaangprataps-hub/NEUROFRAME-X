import pytest
from backend.actiongraph import select_highlights

@pytest.mark.parametrize('duration,expected_max', [
    (2.0, 0.30),   # 2s video → 0.30s budget
    (13.31, 1.9965),
    (30.0, 4.5),
    (120.0, 18.0),
    (600.0, 90.0),
])
def test_budget_enforcement(duration, expected_max):
    # create a set of dummy detections covering the whole video with high confidence
    detections = []
    seg_len = 1.0
    start = 0.0
    while start + seg_len <= duration:
        detections.append({
            'verb': 'take',
            'noun': 'cup',
            'start': round(start, 3),
            'end': round(start + seg_len, 3),
            'confidence': 0.9,
            'label': f'take cup'
        })
        start += seg_len
    highlights = select_highlights(detections, video_duration=duration, target_ratio=0.15)
    total = sum(h['end'] - h['start'] for h in highlights)
    # total must not exceed budget (allow tiny floating error)
    assert total <= expected_max + 1e-6
    # If video is very short and no segment fits, highlights may be empty
    if expected_max < 1.0:
        # ensure we do not artificially create over‑budget segment
        assert total <= expected_max
