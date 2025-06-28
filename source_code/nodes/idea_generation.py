from typing import Dict, Any
from langchain_ollama import OllamaLLM
from utils.database import IdeaDatabase
from config.settings import OLLAMA_MODEL

class IdeaGenerationNode:
    """
    This node generates a new idea for an Instagram Reel video.
    It uses the following components:
    - OllamaLLM: A language model that generates the idea
    - IdeaDatabase: A database that stores past ideas
    """
    def __init__(self):
        self.llm = OllamaLLM(model=OLLAMA_MODEL)
        self.db = IdeaDatabase()
    
    def generate_new_idea(self, past_ideas: list) -> str:
        """Generate a new idea based on past ideas"""
        joined_ideas = "\n".join(past_ideas) if past_ideas else "None yet."
        
        prompt = f"""
        You are a creative AND technical Instagram assistant. Below is a list of past Instagram video topics:

        {joined_ideas}

        Come up with a completely new and original 45-second (MAX 175 WORDS) Instagram video script idea related to AWS services that hasn't been covered yet.

        Your response must include only the raw spoken script — do NOT include a title, do NOT say anything like "Here's a script," and do NOT add any labels, bullet points, or section names. Do not explain what you're doing. Do not add any extra commentary or setup.

        Just start the script as if you're speaking to the camera.

        The script should:
        - Begin with an attention-grabbing hook
        - Explain a specific AWS service in casual, plain English
        - Mention when or why someone would use it
        - Describe in one simple sentence how a developer might set it up or use it

        Speak like you're talking to a tech-savvy friend. Avoid repeating any past topics listed above. Dive right into the script. Nothing else. Please make sure the script is 175 words or less.
        """
        
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            print(f"Error generating idea: {e}")
            # Fallback idea
            return "Hey there! Today I want to talk about AWS Lambda. It's a serverless compute service that runs your code in response to events. Perfect for building scalable applications without managing servers. To get started, just upload your code and AWS handles the rest!"
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the idea generation node"""
        print("Generating new idea...")
        
        try:
            # Get past ideas
            past_ideas = self.db.get_past_ideas()
            
            # Generate new idea
            new_idea = self.generate_new_idea(past_ideas)
            
            # Save to database
            idea_id = self.db.save_idea(new_idea)
            
            # Update state
            state["idea"] = new_idea
            state["idea_id"] = idea_id
            state["past_ideas"] = past_ideas
            
            print(f"✅ Generated idea: {new_idea[:100]}...")
            return state
            
        except Exception as e:
            print(f"Error in idea generation: {e}")
            # Provide a fallback idea
            fallback_idea = "Hey there! Today I want to talk about AWS Lambda. It's a serverless compute service that runs your code in response to events. Perfect for building scalable applications without managing servers. To get started, just upload your code and AWS handles the rest!"
            
            state["idea"] = fallback_idea
            state["idea_id"] = "fallback"
            state["past_ideas"] = []
            
            return state 