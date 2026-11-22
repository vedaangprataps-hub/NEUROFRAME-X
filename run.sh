#!/usr/bin/env bash
set -e

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input_video.mp4> <output_json>"
  exit 1
fi

INPUT="$1"
OUTPUT_JSON="$2"
OUTPUT_MP4="highlights.mp4"

# Run the end‑to‑end pipeline
python -m backend.pipeline "$INPUT" "$OUTPUT_JSON" "$OUTPUT_MP4"

echo "Pipeline completed. JSON: $OUTPUT_JSON, Highlights video: $OUTPUT_MP4"
