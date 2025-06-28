# Instagram Reel Workflow - LangGraph Implementation

## Project Overview

This project automates the creation of Instagram reels about AWS services using AI. It converts a manual Jupyter notebook workflow into a structured, production-ready LangGraph application that generates content ideas, creates audio narration, produces videos with subtitles, and uploads to YouTube.

## Thought Process & Architecture

### The Problem
Creating engaging Instagram content manually is time-consuming and repetitive. The original workflow was scattered across multiple Jupyter notebooks, making it difficult to maintain, debug, and scale.

### The Solution
Convert the workflow into a modular LangGraph application with:
- **Separation of Concerns**: Each step is a separate, testable node
- **State Management**: LangGraph handles data flow between stages
- **Error Handling**: Graceful fallbacks and comprehensive logging
- **Scalability**: Easy to add new nodes or modify existing ones

### Workflow Architecture
```
Idea Generation → Voice Generation → Video Generation → Upload
      ↓                ↓                ↓              ↓
   LLM + DB        TTS + Subtitles   FFmpeg + Video  YouTube API
```

## File Structure

```
ig-reel-workflow/
├── README.md                           # This file
├── research/                           # Original Jupyter notebooks
│   ├── 1_generate_ideas.ipynb         # Original idea generation
│   ├── 2_2_generate_voice.ipynb       # Original voice generation
│   ├── 3_generate_video.ipynb         # Original video generation
│   ├── 4_upload.ipynb                 # Original upload process
│   └── requirements.txt               # Original dependencies
├── source_code/                       # New LangGraph implementation
│   ├── __init__.py                    # Makes source_code a package
│   ├── main.py                        # Entry point for the workflow
│   ├── requirements.txt               # Updated dependencies
│   ├── client_secrets.json            # YouTube API credentials
│   ├── config/                        # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py                # Centralized settings
│   ├── nodes/                         # Workflow node implementations
│   │   ├── __init__.py
│   │   ├── idea_generation.py         # Content idea generation
│   │   ├── voice_generation.py        # Text-to-speech conversion
│   │   ├── video_generation.py        # Video processing
│   │   └── upload.py                  # YouTube upload
│   ├── utils/                         # Utility functions
│   │   ├── __init__.py
│   │   ├── database.py                # Database operations
│   │   └── file_utils.py              # File management
│   └── graph/                         # LangGraph workflow definition
│       ├── __init__.py
│       └── workflow.py                # Main workflow graph
├── output/                            # Generated files (auto-created)
│   ├── output.wav                     # Generated audio
│   ├── output.srt                     # Generated subtitles
│   ├── subway.mp4                     # Background video
│   ├── output_final.mp4               # Final video with audio/subtitles
│   └── output_to_be_up.mp4            # Trimmed video for YouTube
└── vectordb/                          # Vector database storage (auto-created)
```

## Detailed Component Breakdown

### 1. Configuration (`config/settings.py`)

**Purpose**: Centralized configuration management for all components.

**Key Settings**:
- **Model Configuration**: Ollama model selection and parameters
- **Audio Settings**: Sample rate, voice selection, speed
- **Video Settings**: Resolution, duration limits, subtitle styling
- **Path Management**: Output directories and file locations
- **API Configuration**: YouTube API scopes and settings

**Benefits**:
- Single source of truth for all settings
- Easy to modify parameters without touching code
- Environment-specific configuration support

### 2. Database Layer (`utils/database.py`)

**Purpose**: Persistent storage for generated ideas to avoid duplicates.

**Features**:
- **Chroma Vector Database**: Stores ideas with embeddings for similarity search
- **Metadata Management**: Tracks ID, timestamp, and processing status
- **Duplicate Prevention**: Retrieves past ideas to avoid repetition
- **Error Handling**: Graceful fallbacks when database operations fail

**Data Structure**:
```python
{
    "id": "uuid-string",
    "content": "Generated script text",
    "timestamp": "2024-01-01T12:00:00Z",
    "processed": "false"
}
```

### 3. Idea Generation Node (`nodes/idea_generation.py`)

**Purpose**: Generates unique, engaging content ideas for AWS services.

**Process**:
1. **Retrieve Past Ideas**: Gets previous content to avoid duplicates
2. **Craft Prompt**: Creates structured prompt with context and constraints
3. **Generate Content**: Uses Ollama LLM to create new script
4. **Save to Database**: Stores idea with metadata for future reference

**Prompt Engineering**:
- Includes past ideas to avoid repetition
- Specifies content length (175 words max)
- Defines tone (casual, tech-savvy friend)
- Sets structure (hook, explanation, use case, setup)

### 4. Voice Generation Node (`nodes/voice_generation.py`)

**Purpose**: Converts text scripts into natural-sounding audio with synchronized subtitles.

**Process**:
1. **TTS Processing**: Uses Kokoro pipeline for text-to-speech
2. **Chunk Processing**: Breaks audio into manageable segments
3. **Subtitle Generation**: Creates timing-accurate subtitle entries
4. **File Output**: Saves audio (.wav) and subtitles (.srt)

**Technical Details**:
- **Sample Rate**: 24kHz for optimal quality
- **Voice Selection**: Configurable voice and speed parameters
- **Subtitle Formatting**: SRT format with precise timing
- **Text Splitting**: Intelligent line breaks for readability

### 5. Video Generation Node (`nodes/video_generation.py`)

**Purpose**: Combines background video with generated audio and subtitles.

**Process**:
1. **Background Video**: Downloads or uses existing subway video
2. **Audio Integration**: Synchronizes generated audio with video
3. **Subtitle Burning**: Embeds subtitles directly into video
4. **Format Optimization**: Ensures YouTube Shorts compatibility

**Technical Details**:
- **FFmpeg Integration**: Uses imageio-ffmpeg for video processing
- **Subtitle Styling**: Professional styling with background and outline
- **Codec Optimization**: H.264 video, AAC audio for compatibility
- **Aspect Ratio**: 9:16 vertical format for mobile viewing

### 6. Upload Node (`nodes/upload.py`)

**Purpose**: Generates metadata and uploads videos to YouTube.

**Process**:
1. **Metadata Generation**: Creates title and description using LLM
2. **Video Trimming**: Ensures 60-second limit for Shorts
3. **YouTube Upload**: Uses OAuth2 authentication
4. **Status Tracking**: Returns video URL and processing status

**Features**:
- **OAuth2 Authentication**: Secure YouTube API access
- **Metadata Optimization**: SEO-friendly titles and descriptions
- **Error Handling**: Graceful fallback for upload failures
- **Manual Upload Option**: Can skip upload for manual processing

### 7. Workflow Graph (`graph/workflow.py`)

**Purpose**: Orchestrates the entire workflow using LangGraph.

**Structure**:
```python
StateGraph(Dict[str, Any])
├── generate_idea → generate_voice → generate_video → upload
└── State Management: Passes data between nodes automatically
```

**Benefits**:
- **Automatic State Management**: LangGraph handles data flow
- **Error Recovery**: Built-in error handling and retry logic
- **Parallel Processing**: Can be extended for parallel operations
- **Monitoring**: Built-in logging and progress tracking

## Installation & Setup

### Prerequisites
- Python 3.8+
- Ollama with llama3 model
- FFmpeg
- YouTube API credentials (optional)

### Step-by-Step Setup

1. **Clone and Navigate**:
   ```bash
   cd /Users/samihamdalla/Projects/ig-reel-workflow
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv ig-reel-env
   source ig-reel-env/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r source_code/requirements.txt
   ```

4. **Setup Ollama**:
   ```bash
   ollama pull llama3
   ollama serve
   ```

5. **Install FFmpeg** (macOS):
   ```bash
   brew install ffmpeg
   ```

6. **YouTube API Setup** (Optional):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create project and enable YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Download as `client_secrets.json` to `source_code/` directory

### Run the Workflow

```bash
python source_code/main.py
```

## Workflow Execution Flow

### 1. Initialization Phase
```
main.py → InstagramReelWorkflow → StateGraph compilation
```

### 2. Idea Generation Phase
```
Input: Empty state
Process: LLM + Database query
Output: Generated script + metadata
State: {"idea": "script text", "idea_id": "uuid", "past_ideas": [...]}
```

### 3. Voice Generation Phase
```
Input: Script from previous phase
Process: TTS + Subtitle generation
Output: Audio file + SRT file
State: {"audio_path": "path", "subtitle_path": "path"}
```

### 4. Video Generation Phase
```
Input: Audio + Subtitles from previous phase
Process: Video processing + FFmpeg
Output: Final video file
State: {"final_video_path": "path"}
```

### 5. Upload Phase
```
Input: Video from previous phase
Process: Metadata generation + YouTube API
Output: YouTube URL
State: {"video_url": "url", "title": "title", "description": "desc"}
```

## Configuration Options

### Model Settings (`config/settings.py`)
```python
OLLAMA_MODEL = "llama3"              # LLM model for text generation
AUDIO_VOICE = "af_heart"             # TTS voice selection
AUDIO_SPEED = 1.1                    # Speech speed multiplier
VIDEO_MAX_SECONDS = 60               # Maximum video duration
```

### Output Settings
```python
OUTPUT_DIR = "output"                # Generated files directory
PERSIST_DIR = "vectordb"             # Database storage location
```

### Subtitle Styling
```python
SUBTITLE_STYLE = (
    "FontName=Arial,FontSize=20,"
    "PrimaryColour=&Hffffff&,"
    "OutlineColour=&H000000&,"
    "BorderStyle=1,Outline=2"
)
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**:
   ```bash
   # Ensure Ollama is running
   ollama serve
   
   # Check model availability
   ollama list
   ```

2. **FFmpeg Not Found**:
   ```bash
   # Install FFmpeg
   brew install ffmpeg
   
   # Verify installation
   ffmpeg -version
   ```

3. **Database Persistence Issues**:
   - Check `vectordb/` directory permissions
   - Ensure sufficient disk space
   - Verify Chroma installation

4. **YouTube API Errors**:
   - Verify `client_secrets.json` location
   - Check API quota limits
   - Ensure OAuth2 credentials are valid

### Debug Mode
Add debug logging to any node:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Extending the Workflow

### Adding New Nodes
1. Create new node file in `nodes/`
2. Implement `run(state)` method
3. Add to workflow graph in `graph/workflow.py`
4. Update state schema as needed

### Example: Content Filtering Node
```python
class ContentFilterNode:
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        script = state["idea"]
        # Add content filtering logic
        filtered_script = self.filter_content(script)
        state["filtered_idea"] = filtered_script
        return state
```

### Modifying Existing Nodes
- Each node is self-contained and can be modified independently
- State interface defines data contracts between nodes
- Configuration changes only require `settings.py` updates

## Performance Considerations

### Optimization Opportunities
- **Parallel Processing**: Voice and video generation can run in parallel
- **Caching**: Cache background videos and common assets
- **Batch Processing**: Process multiple ideas simultaneously
- **Resource Management**: Monitor memory usage for large videos

### Monitoring
- **Execution Time**: Track time per node
- **Resource Usage**: Monitor CPU, memory, disk usage
- **Error Rates**: Track failure rates per node
- **Output Quality**: Monitor generated content quality

## Future Enhancements

### Planned Features
- **Multi-Platform Support**: TikTok, Instagram, LinkedIn
- **Content Templates**: Pre-defined content structures
- **A/B Testing**: Compare different content variations
- **Analytics Integration**: Track performance metrics
- **Scheduling**: Automated posting at optimal times

### Technical Improvements
- **Database Migration**: Move to PostgreSQL for better scalability
- **API Rate Limiting**: Implement proper rate limiting
- **Content Validation**: Add content quality checks
- **Backup System**: Automated backup of generated content

## Contributing

### Development Workflow
1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings for all classes/methods
- Write unit tests for new functionality


## Acknowledgments

- **LangGraph**: For the workflow orchestration framework
- **Ollama**: For local LLM inference
- **Kokoro**: For high-quality text-to-speech
- **FFmpeg**: For video processing capabilities
- **YouTube API**: For content distribution

---

**Last Updated**: June 28th, 2025  
**Version**: 1.0.0  
**Maintainer**: Sami Hamdalla