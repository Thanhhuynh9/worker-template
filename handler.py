import runpod
import os
import uuid
import subprocess
from pathlib import Path
import requests
from runpod.serverless.utils import rp_upload

def download_file(url, dst):
    r = requests.get(url, stream=True)
    with open(dst, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return dst

def handler(event):
    """
    Run TotalSegmentator using the CLI from inside RunPod Serverless.
    """
    input_url = event["input"].get("input_url")
    task = event["input"].get("task", "total")

    # Create workspace paths
    input_path = f"/workspace/{uuid.uuid4()}.nii.gz"
    output_dir = f"/workspace/output_{uuid.uuid4()}"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Download input file
    download_file(input_url, input_path)

    # 2. Run TotalSegmentator using CLI
    cmd = [
        "TotalSegmentator",
        "-i", input_path,
        "-o", output_dir,
        "--task", task,
        "--fast"
    ]

    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        return {"error": str(e)}

    # 3. Upload all output masks
    output_files = []
    for f in Path(output_dir).glob("*.nii.gz"):
        url = rp_upload(str(f), f.name)
        output_files.append({"file": f.name, "url": url})

    return {
        "status": "completed",
        "task": task,
        "results": output_files
    }

runpod.serverless.start({"handler": handler})
