# Intel Codex CLI - Windows Installation Guide

A powerful AI coding assistant CLI tool configured for Intel's internal Azure OpenAI service.

## System Requirements

- **Windows 10/11** (64-bit)
- **Node.js 22+** (Required)
- **npm** (Comes with Node.js)

## Installation

### Method 1: Automated Installation (Recommended)

1. **Download and extract** the Intel Codex CLI package
2. **Open Command Prompt or PowerShell as Administrator**
3. **Navigate to the extracted folder**:
   ```cmd
   cd "C:\path\to\codex-cli"
   ```
4. **Run the installation script**:
   
   **For Command Prompt:**
   ```cmd
   install-windows.bat
   ```
   
   **For PowerShell:**
   ```powershell
   .\install-windows.ps1
   ```

### Method 2: Manual Installation

1. **Ensure Node.js 22+ is installed**:
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **Navigate to the codex-cli folder** in Command Prompt/PowerShell

3. **Install globally**:
   ```cmd
   npm install -g .
   ```

## Verification

After installation, verify the CLI is working:

1. **Open a new Command Prompt or PowerShell window**
2. **Test the installation**:
   ```cmd
   codex --version
   ```
3. **You should see version information confirming successful installation**

## Usage

The CLI can be used from any directory on your system:

### Basic Usage
```cmd
# Navigate to your project directory
cd "C:\path\to\your\project"

# Ask for help with your code
codex "explain this codebase"
```

### Example Commands
```cmd
# Get code explanations
codex "what does this function do?"

# Request bug fixes
codex "help me fix this error"

# Generate code
codex "add error handling to this function"

# Code review
codex "review this code for potential issues"

# Documentation
codex "add comments to this code"

# Testing
codex "write unit tests for this module"
```

## Features

- ✅ **Pre-configured** for Intel's internal Azure OpenAI service
- ✅ **No API key setup required** - credentials are embedded
- ✅ **Works from any directory** after global installation
- ✅ **Context-aware** - analyzes your current project
- ✅ **Powered by GPT-4** through Intel's Azure deployment
- ✅ **Usage tracking** - automatically tracks CLI usage for Intel metrics

## Privacy and Usage Tracking

This CLI includes built-in usage tracking for Intel internal metrics:

- **What is tracked**: User email (from Intel LDAP), timestamp, and method ('codex')
- **When tracking occurs**: Only once per hour per user to avoid spam
- **Data storage**: Intel's internal MongoDB database (ExpertGPTDB)
- **Privacy**: No code content or prompts are tracked - only usage statistics
- **Failure handling**: If tracking fails (network issues, etc.), the CLI continues normally

The tracking helps Intel understand CLI adoption and usage patterns across the organization.

## Troubleshooting

### Installation Issues

**Error: "Node.js not found"**
- Install Node.js 22+ from https://nodejs.org/
- Restart your terminal after installation

**Error: "Permission denied"**
- Run the installation script as Administrator
- Or use: `npm install -g . --unsafe-perm`

**Error: "npm command not found"**
- Node.js installation may be incomplete
- Reinstall Node.js and restart your terminal

### Usage Issues

**Error: "codex command not found"**
- Close and reopen your terminal after installation
- Verify global npm bin directory is in your PATH
- Run: `npm list -g @intel/codex-cli` to verify installation

**Error: Network or API issues**
- Ensure you're connected to Intel's corporate network
- If using VPN, ensure it allows access to internal Azure services

## Uninstallation

To remove the Intel Codex CLI:

**For Command Prompt:**
```cmd
uninstall-windows.bat
```

**For PowerShell:**
```powershell
.\uninstall-windows.ps1
```

**Or manually:**
```cmd
npm uninstall -g @intel/codex-cli
```

## Support

For technical support or questions:
- Contact your Intel IT support team
- Check internal documentation for additional resources

## Security Notice

This CLI tool contains embedded credentials for Intel's internal Azure OpenAI service. Do not distribute this package outside of Intel or modify the embedded credentials.

---

**Intel Codex CLI v1.0.0**  
*Powered by Azure OpenAI*
