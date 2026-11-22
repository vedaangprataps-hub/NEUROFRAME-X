# NEUROFRAME-X

An AI‑powered action‑aware egocentric video summarization system for the Samsung XR Hackathon 2026.

## Overview
- **Input**: First‑person MP4 video
- **Output**: Highlight video (~15% of original) and JSON evaluation file
- **Core stack**:
  - Backend: FastAPI, OpenCV, FFmpeg, PyTorch
  - Frontend: React + Vite (future work)

## Repository Structure
```
NEUROFRAME X/
│   README.md
│   requirements.txt
│   run.sh
│
├─ backend/
│   │   main.py               # FastAPI entry point
│   │   pipeline.py           # End‑to‑end processing script
│   │   video_ingestion.py    # Video utilities
│   │   action_perception.py  # Model inference
│   │   actiongraph.py        # Highlight selection algorithm
│   │   highlight_generator.py# Clip extraction and concatenation
│   │   schemas.py            # Pydantic models for JSON output
│   
└─ frontend/                 # React app (to be added)
```

## Quick Start (Backend only)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the pipeline on a video:
   ```bash
   ./run.sh input.mp4 output.json
   ```
   This will:
   - Ingest the video
   - Run action inference using a pretrained model
   - Select highlights (≈15% duration)
   - Export `output.json` and `highlights.mp4`

## Development
- Run the API server:
  ```bash
  uvicorn backend.main:app --reload
  ```
- Frontend will be built later (React + Vite).

## License
MIT © 2026 NEUROFRAME‑X team.
