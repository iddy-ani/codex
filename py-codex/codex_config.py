# Create a new file: codex_config.py
# This helps bridge the configuration between your Codex app and Data Agent

import os
from pathlib import Path
from typing import Dict, Any

def get_codex_config() -> Dict[str, Any]:
    """
    Get Codex configuration that's compatible with both apps
    """
    config = {
        # API Configuration
        "api_key": "1ec57c7402ed46ecbae6b09b12cb0e3c",
        "model": "o4-mini",  # Default model
        "timeout": 60.0,
        
        # Memory Configuration
        "memory": {
            "enable_compression": True,
            "compression_threshold_factor": 0.8,
            "keep_recent_messages": 5
        },
        
        # Tool Configuration
        "full_stdout": True,
        "flex_mode": False,
        
        # File System Configuration
        "writable_roots": [str(Path("Outputs").resolve())],
        
        # Instructions/System Prompt
        "instructions": """You are Codex, an AI coding assistant integrated into the Data Agent platform. 
You can help with:
- Writing and debugging code
- Analyzing data files
- Creating scripts and automation
- Explaining technical concepts
- File manipulation and organization

You have access to tools for executing commands and managing files. 
Always ask for permission before making significant changes to files or running potentially destructive commands.

IMPORTANT: After executing any tool, always provide a clear explanation or summary of:
- What the tool did
- What the results show or mean
- Any insights, patterns, or recommendations based on the results
- Next steps or follow-up actions if relevant

When users ask you to analyze, explain, or investigate something, use the available tools to gather information, then provide a comprehensive response based on what you discovered. Never leave the user hanging after a tool execution - always follow up with meaningful analysis and explanation.

Focus on being helpful, accurate, and safe in your code suggestions."""
    }
    
    return config

def validate_codex_setup() -> Dict[str, Any]:
    """
    Validate that Codex can be properly integrated
    """
    status = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
        
    # Check if outputs directory exists
    outputs_dir = Path("Outputs")
    if not outputs_dir.exists():
        try:
            outputs_dir.mkdir(exist_ok=True)
            status["warnings"].append("Created Outputs directory")
        except Exception as e:
            status["errors"].append(f"Cannot create Outputs directory: {e}")
            status["valid"] = False
    
    # Check if Codex modules can be imported
    try:
        # Update this path to match your Codex app location
        import sys
        sys.path.append('path/to/your/codex-agent')  # Update this!
        from core.agent import Agent
        from config import load_config
    except ImportError as e:
        status["errors"].append(f"Cannot import Codex modules: {e}")
        status["valid"] = False
    
    return status

def setup_codex_environment():
    """
    Set up the environment for Codex integration
    """
    # Create necessary directories
    directories = ["Outputs", "Outputs/Codex"]
    for dir_path in directories:
        Path(dir_path).mkdir(exist_ok=True)
    
    # Create a basic .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write("# Add your OpenAI API key here\n")
            f.write("OPENAI_API_KEY=your_api_key_here\n")
        print("Created .env file - please add your OpenAI API key")
    
    print("Codex environment setup complete!")

if __name__ == "__main__":
    # Run validation
    status = validate_codex_setup()
    
    if status["valid"]:
        print("✅ Codex setup is valid!")
        if status["warnings"]:
            for warning in status["warnings"]:
                print(f"⚠️  {warning}")
    else:
        print("❌ Codex setup has issues:")
        for error in status["errors"]:
            print(f"   - {error}")
        
        # Try to set up environment
        print("\nAttempting to set up environment...")
        setup_codex_environment()