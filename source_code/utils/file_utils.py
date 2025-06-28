import os
import subprocess
from pathlib import Path
from typing import List, Dict
from config.settings import OUTPUT_DIR

def cleanup_output_files():
    """Clean up output files after processing"""
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith("output") or filename.startswith("subway"):
            file_path = OUTPUT_DIR / filename
            if file_path.is_file():
                file_path.unlink()
                print(f"Deleted: {file_path}")

def download_subway_video():
    """Download the subway video for background"""
    url = "https://www.youtube.com/watch?v=RbVMiu4ubT0"
    output_path = OUTPUT_DIR / "subway.mp4"
    
    command = (
        'yt-dlp '
        '-f "bv*+ba/b" '
        '--merge-output-format mp4 '
        '--user-agent "Mozilla/5.0" '
        '--no-playlist '
        f'-o "{output_path}" '
        f'"{url}"'
    )
    
    os.system(command)
    return output_path

def trim_video(input_path: Path, max_seconds: int = 60) -> Path:
    """Trim video to specified duration"""
    output_path = OUTPUT_DIR / "output_to_be_up.mp4"
    
    subprocess.run([
        "ffmpeg",
        "-i", str(input_path),
        "-t", str(max_seconds),
        "-vf", "scale=1080:1920",
        "-c:a", "aac",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        str(output_path)
    ], check=True)
    
    return output_path 