import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

class IdeaDatabase:
    """
    Persistent database for storing ideas using Chroma vector database.
    
    This class manages the lifecycle of content ideas from generation through processing.
    Each idea is stored with metadata including unique ID, timestamp, and processing status.
    Uses Chroma for persistent vector storage with Ollama embeddings.
    """
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize Chroma with Ollama embeddings
        self.embeddings = OllamaEmbeddings(model="llama3")
        self.vectorstore = Chroma(
            collection_name="ideas",
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory)
        )
    
    def get_past_ideas(self, limit: int = 100) -> List[str]:
        """Get all past ideas from the database"""
        try:
            results = self.vectorstore.get()
            if not results or not results['documents']:
                return []
            
            # Get the most recent ideas up to the limit
            documents = results['documents'][-limit:]
            return documents
        except Exception as e:
            print(f"Warning: Could not retrieve past ideas: {e}")
            return []
    
    def save_idea(self, idea_text: str) -> str:
        """Save a new idea to the database"""
        unique_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Create metadata
        metadata = {
            "id": unique_id,
            "timestamp": timestamp,
            "processed": "false"
        }
        
        try:
            # Add to vectorstore
            self.vectorstore.add_documents([
                Document(
                    page_content=idea_text,
                    metadata=metadata
                )
            ])
            
            # Chroma automatically persists when using persist_directory
            print(f"Idea saved with ID: {unique_id}")
        except Exception as e:
            print(f"Warning: Could not save idea to database: {e}")
        
        return unique_id
    
    def get_most_recent_unprocessed_idea(self) -> Optional[Document]:
        """Get the most recent unprocessed idea"""
        try:
            # Get all documents
            results = self.vectorstore.get()
            if not results or not results['documents']:
                print("No ideas found in database.")
                return None
            
            # Find unprocessed ideas
            unprocessed_docs = []
            for i, metadata in enumerate(results['metadatas']):
                if metadata and metadata.get('processed') == 'false':
                    unprocessed_docs.append({
                        'content': results['documents'][i],
                        'metadata': metadata,
                        'index': i
                    })
            
            if not unprocessed_docs:
                print("No unprocessed ideas found.")
                return None
            
            # Sort by timestamp and get the most recent
            unprocessed_sorted = sorted(
                unprocessed_docs, 
                key=lambda x: x['metadata']['timestamp'], 
                reverse=True
            )
            most_recent = unprocessed_sorted[0]
            
            document = Document(
                page_content=most_recent['content'],
                metadata=most_recent['metadata']
            )
            
            print(f"Most recent unprocessed idea ID: {most_recent['metadata']['id']}")
            return document
        except Exception as e:
            print(f"Warning: Could not retrieve unprocessed ideas: {e}")
            return None
    
    def mark_idea_as_processed(self, idea_id: str):
        """Mark an idea as processed"""
        try:
            # Get all documents
            results = self.vectorstore.get()
            if not results or not results['metadatas']:
                print(f"Idea {idea_id} not found.")
                return
            
            # Find and update the specific idea
            for i, metadata in enumerate(results['metadatas']):
                if metadata and metadata.get('id') == idea_id:
                    # Update the metadata
                    metadata['processed'] = 'true'
                    
                    # Recreate the collection with updated metadata
                    self.vectorstore.delete_collection()
                    self.vectorstore = Chroma(
                        collection_name="ideas",
                        embedding_function=self.embeddings,
                        persist_directory=str(self.persist_directory)
                    )
                    
                    # Re-add all documents with updated metadata
                    for j, doc in enumerate(results['documents']):
                        if j == i:
                            # Use updated metadata for this document
                            self.vectorstore.add_documents([
                                Document(
                                    page_content=doc,
                                    metadata=metadata
                                )
                            ])
                        else:
                            # Use original metadata for other documents
                            self.vectorstore.add_documents([
                                Document(
                                    page_content=doc,
                                    metadata=results['metadatas'][j]
                                )
                            ])
                    
                    print(f"Marked idea {idea_id} as processed")
                    return
            
            print(f"Idea {idea_id} not found.")
        except Exception as e:
            print(f"Warning: Could not mark idea as processed: {e}")