import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
PERSIST_DIR = BASE_DIR / "vectordb"
OUTPUT_DIR = BASE_DIR / "output"

# Model settings
OLLAMA_MODEL = "llama3"

# Video settings
VIDEO_MAX_SECONDS = 60
VIDEO_RESOLUTION = "1080:1920"  # Vertical 9:16 aspect ratio

# Audio settings
AUDIO_SAMPLE_RATE = 24000
AUDIO_VOICE = "af_heart"
AUDIO_SPEED = 1.1

# Subtitle settings
SUBTITLE_STYLE = (
    "FontName=Arial,"
    "FontSize=20,"
    "PrimaryColour=&Hffffff&,"
    "SecondaryColour=&Hffff00&,"
    "OutlineColour=&H000000&,"
    "BackColour=&H00000000&,"
    "BorderStyle=1,"
    "Outline=2,"
    "Shadow=1,"
    "MarginV=30,"
    "Alignment=2"
)

# YouTube settings
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
YOUTUBE_CATEGORY_ID = "22"

# Create directories if they don't exist
PERSIST_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True) 