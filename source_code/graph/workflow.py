from typing import Dict, Any
from langgraph.graph import StateGraph, END
from nodes.idea_generation import IdeaGenerationNode
from nodes.voice_generation import VoiceGenerationNode
from nodes.video_generation import VideoGenerationNode
from nodes.upload import UploadNode

class InstagramReelWorkflow:
    """
    This workflow is a LangGraph workflow that generates an Instagram Reel video.
    It uses the following nodes:
    - IdeaGenerationNode: Generates an idea for the video
    - VoiceGenerationNode: Generates the voice for the video
    - VideoGenerationNode: Generates the video
    - UploadNode: Uploads the video to YouTube
    """
    def __init__(self):
        self.idea_node = IdeaGenerationNode()
        self.voice_node = VoiceGenerationNode()
        self.video_node = VideoGenerationNode()
        self.upload_node = UploadNode()
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(Dict[str, Any])
        
        # Add nodes
        workflow.add_node("generate_idea", self.idea_node.run)
        workflow.add_node("generate_voice", self.voice_node.run)
        workflow.add_node("generate_video", self.video_node.run)
        workflow.add_node("upload", self.upload_node.run)
        
        # Define the flow
        workflow.set_entry_point("generate_idea")
        workflow.add_edge("generate_idea", "generate_voice")
        workflow.add_edge("generate_voice", "generate_video")
        workflow.add_edge("generate_video", "upload")
        workflow.add_edge("upload", END)
        
        return workflow.compile()
    
    def run(self, initial_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the complete workflow"""
        if initial_state is None:
            initial_state = {}
        
        print(" Starting Instagram Reel Workflow...")
        result = self.workflow.invoke(initial_state)
        
        print("Workflow completed successfully!")
        print(f" Video URL: {result.get('video_url', 'N/A')}")
        
        return result 