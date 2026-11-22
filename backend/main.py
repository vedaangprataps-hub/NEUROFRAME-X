from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Initialize FastAPI app
app = FastAPI()

# Define absolute paths for static directories
BASE_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
TMP_DIR = BASE_DIR / "tmp"

# Ensure directories exist
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files using absolute paths
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
app.mount("/tmp", StaticFiles(directory=str(TMP_DIR)), name="tmp")




@app.post("/process")
async def process(file: UploadFile = File(...)):
    if file.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="Only MP4 videos are supported.")
    # Save uploaded file to a temporary location
    tmp_dir = Path("./tmp")
    tmp_dir.mkdir(exist_ok=True)
    input_path = tmp_dir / file.filename
    with input_path.open("wb") as out_file:
        while content := await file.read(1024 * 1024):
            out_file.write(content)
    output_json = Path("./outputs") / (file.filename.rsplit(".", 1)[0] + ".json")
    output_mp4 = Path("./outputs") / (file.filename.rsplit(".", 1)[0] + "_highlights.mp4")
    try:
        process_video(str(input_path), str(output_json), str(output_mp4))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if input_path.exists():
            input_path.unlink()
    return {
        "json": str(output_json),
        "highlights": str(output_mp4)
    }
