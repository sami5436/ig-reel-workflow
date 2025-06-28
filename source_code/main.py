from pathlib import Path
import sys

# Add the source_code directory to the Python path
sys.path.append(str(Path(__file__).parent))

from graph.workflow import InstagramReelWorkflow
from utils.file_utils import cleanup_output_files

def main():
    """Main entry point for the Instagram Reel Workflow"""
    try:
        # Create and run the workflow
        workflow = InstagramReelWorkflow()
        result = workflow.run()
        
        print("\n" + "="*50)
        print("🎬 WORKFLOW SUMMARY")
        print("="*50)
        print(f"Idea: {result.get('idea', 'N/A')[:100]}...")
        print(f"Audio: {result.get('audio_path', 'N/A')}")
        print(f"Video: {result.get('final_video_path', 'N/A')}")
        print(f"YouTube URL: {result.get('video_url', 'N/A')}")
        print("="*50)
        
        # Clean up temporary files
        print("\n Cleaning up temporary files...")
        cleanup_output_files()
        
    except Exception as e:
        print(f"Error running workflow: {e}")
        raise

if __name__ == "__main__":
    main() 