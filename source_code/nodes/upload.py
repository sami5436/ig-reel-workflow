import subprocess
from pathlib import Path
from typing import Dict, Any
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from langchain_ollama import OllamaLLM
from utils.file_utils import trim_video
from config.settings import OUTPUT_DIR, OLLAMA_MODEL, YOUTUBE_SCOPES, YOUTUBE_CATEGORY_ID

class UploadNode:
    """
    Handles video upload to YouTube with AI-generated titles and descriptions.
    
    This node processes the final video by generating engaging titles and descriptions
    using an LLM, trimming the video for YouTube Shorts format, and uploading it
    to YouTube using the YouTube Data API v3.
    
    Features:
    - AI-powered title and description generation
    - YouTube Shorts video trimming
    - YouTube API integration for uploads
    - OAuth2 authentication handling
    - Error handling for missing credentials
    
    Outputs:
    - YouTube video URL
    """
    def __init__(self):
        self.llm = OllamaLLM(model=OLLAMA_MODEL)
        # Get the path to the source_code directory
        self.source_code_dir = Path(__file__).parent.parent
    
    def generate_video_title(self, script: str) -> str:
        """Generate a title for the video"""
        prompt = f"""You are a helpful assistant. You really know your stuff. Generate a title for the following script: {script} Keep it short and concise something like this AWS Tip: CloudFront Made Simple. I need to make sure it is something that will be interesting to the audience and only 6 words.Give me the title only, no other text. Nothing else. literally. choose the best title for the script. no quotes even just the text. please make sure no quotes or anything else. just the text."""
        return self.llm.invoke(prompt)
    
    def generate_video_description(self, script: str) -> str:
        """Generate a description for the video"""
        prompt = f"""Generate a description for the following script: {script} Keep it short and concise something like this: Here's how CloudFront boosts your AWS app performance in seconds. Learn, deploy, repeat. #AWS #Tech. Do not include any other text. Nothing else. literally. choose the best description for the script. Choose the best description for the script. I only want one. Give me one response. no quotes even just the text. please make sure no quotes or anything else. just the text."""
        return self.llm.invoke(prompt)
    
    def upload_to_youtube(self, video_path: Path, title: str, description: str) -> str:
        """Upload video to YouTube"""
        print("Uploading to YouTube...")
        
        # Use the correct path to client_secrets.json
        client_secrets_path = self.source_code_dir / "client_secrets.json"
        
        if not client_secrets_path.exists():
            print(f"client_secrets.json not found at: {client_secrets_path}")
            print("Please make sure you have set up YouTube API credentials.")
            return "Upload skipped - no credentials found"
        
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), YOUTUBE_SCOPES)
        creds = flow.run_local_server(port=0)
        
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
        
        request_body = {
            "snippet": {
                "categoryId": YOUTUBE_CATEGORY_ID,
                "title": f"{title} #Shorts",
                "description": description
            },
            "status": {
                "privacyStatus": "public"
            }
        }
        
        media_file = MediaFileUpload(str(video_path))
        
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        )
        
        response = request.execute()
        video_url = f"https://youtube.com/watch?v={response['id']}"
        print(f"Uploaded to: {video_url}")
        return video_url
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the upload node"""
        script = state["idea"]
        final_video_path = state["final_video_path"]
        
        # Generate title and description
        print("Generating title and description...")
        title = self.generate_video_title(script)
        description = self.generate_video_description(script)
        
        print(f"Title: {title}")
        print(f"Description: {description}")
        
        # Trim video for YouTube Shorts
        trimmed_path = trim_video(final_video_path)
        
        # Upload to YouTube
        video_url = self.upload_to_youtube(trimmed_path, title, description)
        
        # Update state
        state["title"] = title
        state["description"] = description
        state["video_url"] = video_url
        state["trimmed_video_path"] = trimmed_path
        
        print("Upload completed successfully")
        return state 