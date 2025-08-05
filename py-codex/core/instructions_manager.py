# instructions_manager.py
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class InstructionsManager:
    """Manages custom instructions for the Codex agent"""
    
    def __init__(self):
        # Create instructions directory in user's home folder
        self.base_dir = Path.home() / ".dataagent"
        self.instructions_dir = self.base_dir / "instructions"
        self.config_file = self.base_dir / "instructions_config.json"
        
        # Ensure directories exist
        self.instructions_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default instruction if none exist
        self._ensure_default_instructions()
    
    def _ensure_default_instructions(self):
        """Create default instructions if directory is empty"""
        if not any(self.instructions_dir.glob("*.md")):
            default_content = """# Default Codex Instructions

You are Codex, an AI coding assistant integrated into the Data Agent platform. 

## Your Capabilities
- Writing and debugging code in multiple languages
- Analyzing data files and creating visualizations
- Creating scripts and automation tools
- Explaining technical concepts clearly
- File manipulation and organization
- Command-line operations and system administration

## Guidelines
- Always ask for permission before making significant changes to files
- Provide clear explanations of what your tools do and what the results mean
- When analyzing data, always follow up with insights and recommendations
- Be helpful, accurate, and prioritize safety in all suggestions
- Focus on practical, working solutions

## Tool Usage
After executing any tool, always provide:
1. What the tool accomplished
2. Interpretation of the results
3. Any insights or patterns discovered
4. Recommended next steps

Remember: You're here to help users be more productive with their coding and data analysis tasks!
"""
            self.save_instruction("default", default_content)
    
    def get_instructions_list(self) -> List[Dict[str, str]]:
        """Get list of all available instruction files"""
        instructions = []
        for file_path in self.instructions_dir.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title from first line if it's a header
                lines = content.split('\n')
                title = lines[0].replace('# ', '').strip() if lines and lines[0].startswith('# ') else file_path.stem
                
                instructions.append({
                    'filename': file_path.stem,
                    'title': title,
                    'path': str(file_path),
                    'size': len(content),
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
            except Exception as e:
                print(f"Error reading instruction file {file_path}: {e}")
                continue
        
        return sorted(instructions, key=lambda x: x['filename'])
    
    def get_instruction_content(self, filename: str) -> Optional[str]:
        """Get content of a specific instruction file"""
        file_path = self.instructions_dir / f"{filename}.md"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading instruction file {filename}: {e}")
            return None
    
    def save_instruction(self, filename: str, content: str) -> bool:
        """Save instruction content to file"""
        try:
            # Sanitize filename
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_filename:
                safe_filename = "untitled"
            
            file_path = self.instructions_dir / f"{safe_filename}.md"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving instruction file {filename}: {e}")
            return False
    
    def delete_instruction(self, filename: str) -> bool:
        """Delete an instruction file"""
        if filename == "default":
            return False  # Don't allow deleting default
        
        file_path = self.instructions_dir / f"{filename}.md"
        if not file_path.exists():
            return False
        
        try:
            file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting instruction file {filename}: {e}")
            return False
    
    def get_selected_instruction(self) -> str:
        """Get the currently selected instruction filename"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return config.get('selected_instruction', 'default')
            except:
                pass
        return 'default'
    
    def set_selected_instruction(self, filename: str) -> bool:
        """Set the currently selected instruction"""
        try:
            config = {'selected_instruction': filename}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error setting selected instruction: {e}")
            return False
    
    def get_current_instructions(self) -> str:
        """Get the content of currently selected instructions"""
        selected = self.get_selected_instruction()
        content = self.get_instruction_content(selected)
        return content or self.get_instruction_content('default') or ""

# Global instance
instructions_manager = InstructionsManager()