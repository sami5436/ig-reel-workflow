import subprocess
import imageio_ffmpeg
from pathlib import Path
from typing import Dict, Any
from utils.file_utils import download_subway_video
from config.settings import OUTPUT_DIR, SUBTITLE_STYLE

class VideoGenerationNode:
    """
    Combines background video with generated audio and subtitles to create final video.
    
    This node takes the generated audio and subtitle files from the voice generation
    process and merges them with a background video to create the final output video.
    It handles video downloading, audio synchronization, and subtitle burning using
    FFmpeg for professional-quality video production.
    
    Features:
    - Background video management and downloading
    - Audio-video synchronization
    - Subtitle burning with custom styling
    - FFmpeg-based video processing
    - File size reporting and error handling
    
    Outputs:
    - Final MP4 video with audio and burned-in subtitles
    """
    
    def __init__(self):
        self.video_path = None
    
    def download_background_video(self) -> Path:
        """Download background video if not already present"""
        video_path = OUTPUT_DIR / "subway.mp4"
        if not video_path.exists():
            print("Downloading background video...")
            download_subway_video()
        return video_path
    
    def burn_audio_and_subtitles(self, video_path: Path, audio_path: Path, subtitle_path: Path) -> Path:
        """Burn audio and subtitles into video"""
        print("🎬 Processing video with audio and subtitles...")
        
        output_path = OUTPUT_DIR / "output_final.mp4"
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        command = [
            ffmpeg_path,
            "-i", str(video_path),
            "-i", str(audio_path),
            "-vf", f"subtitles={subtitle_path}:force_style='{SUBTITLE_STYLE}'",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-y",
            str(output_path)
        ]
        
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Final video saved to {output_path}")
            
            if output_path.exists():
                file_size = output_path.stat().st_size / (1024 * 1024)  # MB
                print(f"Output file size: {file_size:.1f} MB")
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e}")
            print(f"Error output: {e.stderr}")
            raise
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the video generation node"""
        # Download background video
        video_path = self.download_background_video()
        
        # Get paths from state
        audio_path = state["audio_path"]
        subtitle_path = state["subtitle_path"]
        
        # Burn audio and subtitles
        final_video_path = self.burn_audio_and_subtitles(video_path, audio_path, subtitle_path)
        
        # Update state
        state["final_video_path"] = final_video_path
        
        print("Video generation completed")
        return state 