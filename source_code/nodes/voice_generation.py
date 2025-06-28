import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, Any, List
from kokoro import KPipeline
from config.settings import OUTPUT_DIR, AUDIO_SAMPLE_RATE, AUDIO_VOICE, AUDIO_SPEED

class VoiceGenerationNode:
    """
    Converts text scripts into audio and generates synchronized subtitles.
    
    This node uses the Kokoro TTS pipeline to transform written content into
    natural-sounding speech while creating precise subtitle timing information.
    It processes the script in chunks, generating audio segments and corresponding
    subtitle entries with accurate timestamps for video synchronization.
    
    Features:
    - Text-to-speech conversion using Kokoro TTS
    - Automatic subtitle generation with timing
    - Audio chunk processing for better quality
    - SRT subtitle file creation
    - Configurable voice, speed, and sample rate
    
    Outputs:
    - WAV audio file with generated speech
    - SRT subtitle file with synchronized timing
    """
    
    def __init__(self):
        self.pipeline = KPipeline(lang_code='a')
    
    def generate_audio_and_subtitles(self, script: str) -> Dict[str, Any]:
        """Generate audio and subtitles from script"""
        print("Generating audio and subtitles...")
        
        # Generate audio from script
        generator = self.pipeline(script, voice=AUDIO_VOICE, speed=AUDIO_SPEED)
        
        # Collect audio chunks and timing information
        audio_chunks = []
        subtitle_entries = []
        current_time = 0.0
        
        for i, (graphemes, phonemes, audio) in enumerate(generator):
            audio_chunks.append(audio)
            
            # Calculate timing for subtitles
            chunk_duration = len(audio) / AUDIO_SAMPLE_RATE
            start_time = current_time
            end_time = current_time + chunk_duration
            
            # Split long text into smaller subtitle chunks
            words = graphemes.split()
            subtitle_lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= 50:
                    current_line += (" " + word) if current_line else word
                else:
                    if current_line:
                        subtitle_lines.append(current_line)
                    current_line = word
            
            if current_line:
                subtitle_lines.append(current_line)
            
            # If text is short enough, keep as single subtitle
            if len(subtitle_lines) <= 2:
                subtitle_lines = [graphemes]
            
            # Create subtitle entries for each line
            line_duration = chunk_duration / len(subtitle_lines)
            for j, line in enumerate(subtitle_lines):
                line_start_time = start_time + (j * line_duration)
                line_end_time = start_time + ((j + 1) * line_duration)
                
                # Format times for SRT
                line_start_str = f"{int(line_start_time//3600):02d}:{int((line_start_time%3600)//60):02d}:{int(line_start_time%60):02d},{int((line_start_time%1)*1000):03d}"
                line_end_str = f"{int(line_end_time//3600):02d}:{int((line_end_time%3600)//60):02d}:{int(line_end_time%60):02d},{int((line_end_time%1)*1000):03d}"
                
                subtitle_entries.append({
                    'index': len(subtitle_entries) + 1,
                    'start_time': line_start_str,
                    'end_time': line_end_str,
                    'text': line.strip()
                })
            
            current_time = end_time
            print(f"Chunk {i}: {graphemes}")
        
        return {
            "audio_chunks": audio_chunks,
            "subtitle_entries": subtitle_entries
        }
    
    def save_audio_and_subtitles(self, audio_chunks: List, subtitle_entries: List) -> Dict[str, Path]:
        """Save audio and subtitle files"""
        # Combine audio chunks
        if audio_chunks:
            combined_audio = np.concatenate(audio_chunks)
            audio_path = OUTPUT_DIR / "output.wav"
            sf.write(str(audio_path), combined_audio, AUDIO_SAMPLE_RATE)
            print(f"Generated {audio_path} with {len(audio_chunks)} chunks")
        
        # Create SRT subtitle file
        subtitle_path = OUTPUT_DIR / "output.srt"
        with open(subtitle_path, "w", encoding="utf-8") as f:
            for entry in subtitle_entries:
                f.write(f"{entry['index']}\n")
                f.write(f"{entry['start_time']} --> {entry['end_time']}\n")
                f.write(f"{entry['text']}\n\n")
        
        print(f"Generated {subtitle_path} with {len(subtitle_entries)} subtitle entries")
        
        return {
            "audio_path": audio_path,
            "subtitle_path": subtitle_path
        }
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the voice generation node"""
        script = state["idea"]
        
        # Generate audio and subtitles
        result = self.generate_audio_and_subtitles(script)
        
        # Save files
        file_paths = self.save_audio_and_subtitles(
            result["audio_chunks"], 
            result["subtitle_entries"]
        )
        
        # Update state
        state["audio_path"] = file_paths["audio_path"]
        state["subtitle_path"] = file_paths["subtitle_path"]
        
        print("Audio and subtitles generated successfully")
        return state 