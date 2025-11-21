from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from totalsegmentator.server import TotalSegmentatorServer
import tempfile
import os
import shutil
from pathlib import Path

app = FastAPI()

# Load model once at startup
seg = TotalSegmentatorServer(device="cuda", fast=True, rope=True, ml=True)

@app.post("/segment")
async def segment(file: UploadFile = File(...)):
    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".nii.gz") as tmp:
        content = await file.read()
        tmp.write(content)
        input_path = tmp.name

    output_dir = tempfile.mkdtemp()
    try:
        seg.segment(input_path, output_dir, task="total")
        result_path = next(Path(output_dir).glob("*.nii.gz"))
        return StreamingResponse(
            open(result_path, "rb"),
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=segmentation.nii.gz"}
        )
    finally:
        os.unlink(input_path)
        shutil.rmtree(output_dir, ignore_errors=True)
