# Intel ExpertGPT Codex CLI - User Guide

## Overview

Intel ExpertGPT Codex CLI is a powerful AI-powered coding assistant that runs directly in your terminal. Built on OpenAI's latest reasoning models, it can read, modify, and execute code on your local machine to help you build features faster, fix bugs, and understand complex codebases.

**Key Benefits:**
- 🚀 **Zero API key setup** - pre-configured for Intel's Azure OpenAI service
- 🔒 **Secure** - runs locally, code stays on your machine
- ⚡ **Fast** - direct terminal integration for quick iteration
- 🎯 **Intelligent** - understands your entire project context
- 🛡️ **Safe** - sandboxed execution with approval controls

---

## Quick Start

### Installation

1. **Extract** the `intel-codex-cli-windows` package
2. **Run** `QUICK-INSTALL.bat` as Administrator
3. **Open** a new Command Prompt or PowerShell window
4. **Navigate** to your project: `cd C:\path\to\your\project`
5. **Start coding** with AI: `codex "explain this codebase"`

### First Commands

```cmd
# Interactive mode - opens a chat interface
codex

# Direct prompt - get immediate help
codex "fix any build errors"

# With specific instructions
codex "add error handling to the main function"
```

---

## Approval Modes

Intel ExpertGPT Codex CLI offers three distinct approval modes to control how much autonomy you give the AI:

| Mode | Command | What It Does | Best For |
|------|---------|--------------|----------|
| **Suggest** (Default) | `codex` | Proposes changes but asks for approval before making any modifications or running commands | Learning codebases, code reviews, safe exploration |
| **Auto Edit** | `codex --auto-edit` | Automatically reads and writes files, but still asks before running shell commands | Refactoring, repetitive edits where you want to monitor side effects |
| **Full Auto** | `codex --full-auto` | Autonomously reads, writes, and executes commands in a sandboxed environment | Complex tasks like fixing builds or prototyping while you step away |

### Switching Modes During a Session

You can change modes anytime during a Codex session:
- Type `/mode` to see current mode and options
- Type `/suggest`, `/auto-edit`, or `/full-auto` to switch modes

---

## Available Models

Intel ExpertGPT Codex CLI provides access to multiple AI models, each optimized for different use cases:

### **Reasoning Models** (Recommended)
- **o3** - Flagship multimodal reasoning model, excellent for complex coding tasks
- **o3-mini** - Cost-effective reasoning model, 90% cheaper than O3
- **o3-pro** - Maximum reasoning power for the most complex problems

### **Fast Models**
- **gpt-4.1-nano** - Ultra-fast, sub-second latency for simple tasks
- **gpt-4.1-mini** - Balanced speed and quality, 26% cheaper than GPT-4o
- **gpt-4.1** - Latest flagship with 1M token context, excellent for code diffs

### **Specialized Models**
- **codex-mini** - Specialized for code completion and generation
- **gpt-4o** - Real-time multimodal model with low latency
- **gpt-4** - High-quality model with vision capabilities

### **Legacy Models**
- **o1** - Advanced reasoning model for complex STEM and coding
- **gpt-4.5-preview** - Research preview bridging GPT-4 to GPT-5
- **gpt-35-turbo** - Fast, cost-effective model for lightweight tasks

### Using Different Models

```cmd
# Use a specific model
codex --model o3 "complex algorithm optimization"

# Use mini for quick tasks
codex --model o3-mini "add comments to this function"

# Use nano for instant responses
codex --model gpt-4.1-nano "what does this variable do?"
```

---

## Authentication & API Keys

### Intel Network (Default)
**No API key required!** Intel ExpertGPT Codex CLI comes pre-configured with access to Intel's internal Azure OpenAI service. Just install and start using.

### Using Your Own OpenAI Account (Optional)
If you prefer to use your personal OpenAI account:

```cmd
# Set your API key
set OPENAI_API_KEY=your-api-key-here

# Use with OpenAI provider
codex --provider openai "your prompt"
```

**Important:** Never share or expose API keys. The Intel-provided service doesn't require any key management.

---

## Common Usage Patterns

### Code Understanding
```cmd
codex "explain this codebase to me"
codex "what does this function do?"
codex "show me the data flow through this module"
```

### Bug Fixing
```cmd
codex "find and fix any bugs in this code"
codex "this function is throwing an error, please debug"
codex "fix the build issues in this project"
```

### Code Generation
```cmd
codex "write unit tests for this module"
codex "add error handling to this function"
codex "create a REST API endpoint for user management"
```

### Refactoring
```cmd
codex "refactor this class to use modern patterns"
codex "optimize this algorithm for better performance"
codex "convert this code to TypeScript"
```

### Documentation
```cmd
codex "add comprehensive comments to this code"
codex "generate API documentation"
codex "create a README for this project"
```

---

## Advanced Features

### Multimodal Input
Share screenshots or diagrams to help Codex understand your requirements:

```cmd
codex --image screenshot.png "implement this UI design"
codex --image diagram.jpg "create code based on this architecture"
```

### Project Context
Codex automatically understands your project structure and can work across multiple files:

```cmd
codex "update all components to use the new API"
codex "find all TODO comments and implement them"
```

### Git Integration
Codex works seamlessly with version control:

```cmd
codex "review my recent changes and suggest improvements"
codex "create a commit message for these changes"
```

---

## Safety & Security

### Sandboxed Execution
In **Full Auto** mode, Codex runs commands in a secure sandbox that:
- ✅ Can read any file in your project
- ✅ Can write files in your project directory
- ❌ Cannot access network (prevents data leaks)
- ❌ Cannot modify files outside your project

### Data Privacy
- Your code **never leaves** your machine
- Only prompts and high-level context are sent to the AI
- All file operations happen locally
- Intel's internal Azure service ensures data stays within Intel infrastructure

---

## Troubleshooting

### Installation Issues
```cmd
# Check if installed correctly
codex --version

# Reinstall if needed
cd path\to\intel-codex-cli-windows
npm install -g .
```

### Performance Issues
```cmd
# Use faster models for simple tasks
codex --model gpt-4.1-nano "quick question"

# Check system resources
# Codex requires 4GB RAM minimum, 8GB recommended
```

### Network Issues
```cmd
# Intel network should work automatically
# If issues persist, contact IT support
```

### Getting Unstuck
```cmd
# Cancel current operation
Ctrl+C

# Ask Codex to continue from where it left off
codex "continue from the previous step"

# Reset and start fresh
codex "start over with a simpler approach"
```

---

## Best Practices

### Effective Prompting
- **Be specific**: "Add error handling to the login function" vs "improve this code"
- **Provide context**: "This is a React component for user authentication"
- **Set constraints**: "Keep the existing API structure but improve performance"

### Project Organization
- Use descriptive file and folder names
- Include a README.md in your project root
- Add comments for complex business logic

### Version Control
- Always work in a Git repository
- Commit your work before major Codex sessions
- Review Codex's changes before committing

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Cancel current operation |
| `Enter` | Send message or approve action |
| `n` + `Enter` | Reject proposed change |
| `y` + `Enter` | Approve proposed change |
| `/help` | Show available commands |
| `/mode` | Change approval mode |
| `/exit` | Exit Codex session |

---

## Examples by Use Case

### Frontend Development
```cmd
codex "create a responsive navigation component"
codex "add dark mode toggle to this React app"
codex "optimize this component for better performance"
```

### Backend Development
```cmd
codex "create a RESTful API for user management"
codex "add authentication middleware"
codex "optimize this database query"
```

### DevOps & Build Issues
```cmd
codex --full-auto "fix the CI/CD pipeline"
codex "configure Docker for this application"
codex "resolve dependency conflicts"
```

### Testing
```cmd
codex "write comprehensive unit tests"
codex "create integration tests for this API"
codex "add test coverage for edge cases"
```

---

## Getting Help

### In-Session Help
```cmd
# Type in any Codex session
/help           # Show available commands
/commands       # List all slash commands
/examples       # Show usage examples
```

### Command Line Help
```cmd
codex --help    # Show all available options
codex --version # Show current version
```

### Support Resources
- **Internal Intel Documentation**: Check your team's wiki or internal resources
- **GitHub Repository**: [https://github.com/openai/codex](https://github.com/openai/codex)
- **IT Support**: Contact your Intel IT support team for installation issues

---

## Tips for Success

1. **Start Small**: Begin with simple tasks to understand how Codex works
2. **Be Interactive**: Use Suggest mode first, then graduate to Auto Edit or Full Auto
3. **Review Everything**: Always review Codex's changes before accepting them
4. **Use Version Control**: Commit frequently so you can easily revert if needed
5. **Experiment with Models**: Try different models for different task types
6. **Provide Context**: The more context you give, the better results you'll get

---

**Happy coding with Intel ExpertGPT Codex CLI! 🚀**

*For technical support or questions, contact your Intel IT support team.*
