import os
import subprocess
import sys
import shutil
from pathlib import Path
from typing import List, Dict

def _ffmpeg_extract(input_path: str, start: float, end: float, out_path: str):
    """Extract a clip from input_path between start and end seconds to out_path using ffmpeg.
    """
    duration = end - start
    cmd = [
        "ffmpeg",
        "-y",  # overwrite output if exists
        "-i", input_path,
        "-ss", f"{start:.3f}",
        "-t", f"{duration:.3f}",
        "-c", "copy",
        out_path,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def generate_highlights_video(input_path: str, highlights: List[Dict], output_path: str):
    """Generate a highlights video by concatenating selected segments.

    Args:
        input_path: Path to the original video.
        highlights: List of dicts with 'start' and 'end' (seconds).
        output_path: Destination MP4 path for the concatenated highlights.
    """
    if not highlights:
        raise ValueError("No highlights provided for video generation")

    # Ensure ffmpeg is available; if not, raise an error.
    if shutil.which('ffmpeg') is None:
        raise FileNotFoundError('ffmpeg not found in PATH. Install FFmpeg from https://ffmpeg.org/download.html and ensure it is accessible.')

    tmp_dir = Path("./tmp_highlights")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    segment_files: List[str] = []
    for idx, seg in enumerate(highlights):
        seg_path = tmp_dir / f"seg_{idx}.mp4"
        _ffmpeg_extract(input_path, seg["start"], seg["end"], str(seg_path))
        segment_files.append(str(seg_path))

    # Create a file list for ffmpeg concat
    list_path = tmp_dir / "segments.txt"
    with list_path.open("w", encoding="utf-8") as f:
        for fp in segment_files:
            f.write(f"file '{fp}'\n")

    concat_cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_path),
        "-c", "copy",
        output_path,
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Clean up temporary segment files
    for fp in segment_files:
        try:
            os.remove(fp)
        except OSError:
            pass
    try:
        list_path.unlink()
        tmp_dir.rmdir()
    except OSError:
        pass
