# Intel Codex CLI - Update System Administration Guide

## Overview

The Intel Codex CLI includes an automatic update system that checks for updates on startup from a network share. This allows for centralized distribution of updates across the Intel organization.

## Network Share Setup

### Location
- **Network Share**: `\\IREGPT1\Codex`
- **Required Files**: 
  - `intel-codex-cli-windows.zip` (latest package)
  - `update-info.json` (version metadata)

### Required Permissions
- **Read Access**: All Intel engineers who use Codex CLI
- **Write Access**: IT administrators who deploy updates

## Deploying Updates

### Method 1: Automated Deployment (Recommended)

1. **Navigate** to the codex-cli development directory
2. **Update version** in `package.json`
3. **Run deployment script**:
   ```cmd
   deploy-update.bat
   ```

This script will:
- Build the latest version
- Create a distribution package
- Zip the package
- Copy to network share
- Generate update-info.json
- Clean up temporary files

### Method 2: Manual Deployment

1. **Build distribution package**:
   ```cmd
   create-distribution.bat
   ```

2. **Create zip file**:
   ```cmd
   powershell -Command "Compress-Archive -Path 'intel-codex-cli-windows' -DestinationPath 'intel-codex-cli-windows.zip' -Force"
   ```

3. **Copy to network share**:
   ```cmd
   copy intel-codex-cli-windows.zip \\IREGPT1\Codex\
   ```

4. **Create/update update-info.json** (see format below)

5. **Copy update info**:
   ```cmd
   copy update-info.json \\IREGPT1\Codex\
   ```

## Update Info Format

The `update-info.json` file controls how updates are presented to users:

```json
{
  "version": "1.1.0",
  "releaseDate": "2025-08-06",
  "downloadUrl": "\\\\IREGPT1\\Codex\\intel-codex-cli-windows.zip",
  "changelog": [
    "Added automatic update system",
    "Improved user tracking",
    "Enhanced error handling",
    "Added support for new models"
  ],
  "required": false
}
```

### Fields Explanation

- **version**: Semantic version number (must be higher than current version)
- **releaseDate**: Human-readable release date
- **downloadUrl**: Network path to the update package
- **changelog**: Array of user-friendly change descriptions
- **required**: Boolean - if true, users cannot skip this update

## Update Behavior

### On Startup
1. CLI checks if network share is accessible
2. Reads `update-info.json` if available
3. Compares current version with available version
4. Prompts user if update is available (unless skipped)

### User Options
- **Y**: Install update immediately
- **N**: Skip this time (will prompt again next startup)
- **S**: Skip this version permanently (won't prompt for this version again)

### Required Updates
- If `"required": true`, users cannot skip
- CLI will exit after installing required updates
- Users must restart to continue

## Update Process

1. **Download**: Package is copied from network share to temp directory
2. **Extract**: Zip file is extracted using PowerShell
3. **Install**: `npm install -g` installs the update globally
4. **Cleanup**: Temporary files are removed
5. **Restart**: For required updates, CLI exits for restart

## Troubleshooting

### Network Share Issues
```
ERROR: Cannot access network share \\IREGPT1\Codex
```
**Solutions**:
- Verify network connectivity
- Check share permissions
- Ensure share is mounted/accessible
- Contact IT support

### Update Download Failures
```
ERROR: Update package not found on network share
```
**Solutions**:
- Verify `intel-codex-cli-windows.zip` exists on share
- Check file permissions
- Ensure file is not corrupted

### Installation Failures
```
ERROR: Failed to install update
```
**Solutions**:
- Ensure user has npm global install permissions
- Check if CLI is currently running (close all instances)
- Run as Administrator if needed
- Verify disk space availability

## Version Management

### Semantic Versioning
Use semantic versioning (major.minor.patch):
- **Major**: Breaking changes requiring user action
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, minor improvements

### Required vs Optional Updates
- **Required**: Security fixes, critical bug fixes, breaking changes
- **Optional**: Feature additions, performance improvements, minor fixes

### Version Skipping
- Users can permanently skip non-required versions
- Skipped versions are stored in `~/.codex/skipped-versions.json`
- IT can force updates by setting `"required": true`

## Security Considerations

### Network Share Security
- Ensure only authorized personnel can write to `\\IREGPT1\Codex`
- Verify file integrity before deployment
- Use proper access controls

### Update Verification
- Test updates in development environment first
- Verify zip file integrity
- Check update-info.json format

### Rollback Procedures
- Keep previous versions available for rollback
- Document rollback procedures
- Test rollback scenarios

## Monitoring and Analytics

### Update Adoption
- Monitor network share access logs
- Track version adoption rates
- Identify users not updating

### Error Tracking
- Review CLI logs for update failures
- Monitor help desk tickets related to updates
- Track common update issues

## Best Practices

### Deployment Schedule
- Deploy during low-usage periods
- Announce major updates in advance
- Stagger required updates if needed

### Testing
- Test updates on multiple Windows configurations
- Verify network share accessibility
- Test both required and optional update flows

### Communication
- Notify users of upcoming required updates
- Provide changelog information
- Maintain update documentation

## Example Deployment Workflow

1. **Development**:
   ```cmd
   # Update version in package.json
   # Test locally
   # Commit changes
   ```

2. **Build and Deploy**:
   ```cmd
   deploy-update.bat
   ```

3. **Verification**:
   ```cmd
   # Check files on network share
   dir \\IREGPT1\Codex
   
   # Test update process
   codex --version
   ```

4. **Monitoring**:
   - Watch for user feedback
   - Monitor update adoption
   - Address any issues

---

**For technical support or questions about the update system, contact the Intel Codex CLI administration team.**
