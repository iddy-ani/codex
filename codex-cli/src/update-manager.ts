import fs from 'fs';
import path from 'path';
import os from 'os';
import { execSync } from 'child_process';

interface UpdateInfo {
  version: string;
  releaseDate: string;
  downloadUrl: string;
  changelog: string[];
  required: boolean;
}

class UpdateManager {
  private readonly networkShare = '\\\\IREGPT1\\Codex';
  private readonly updateInfoFile = 'update-info.json';
  private readonly packageFile = 'intel-codex-cli-windows.zip';
  private readonly currentVersion: string;

  constructor() {
    // Get current version from package.json
    try {
      const packageJsonPath = path.join(__dirname, '..', '..', 'package.json');
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
      this.currentVersion = packageJson.version;
    } catch (error) {
      this.currentVersion = '1.0.0'; // fallback
    }
  }

  private async checkNetworkShareAccess(): Promise<boolean> {
    try {
      // Try to access the network share
      fs.accessSync(this.networkShare, fs.constants.R_OK);
      return true;
    } catch (error) {
      return false;
    }
  }

  private async getUpdateInfo(): Promise<UpdateInfo | null> {
    try {
      const updateInfoPath = path.join(this.networkShare, this.updateInfoFile);
      
      if (!fs.existsSync(updateInfoPath)) {
        return null;
      }

      const updateInfoContent = fs.readFileSync(updateInfoPath, 'utf-8');
      const updateInfo: UpdateInfo = JSON.parse(updateInfoContent);
      
      return updateInfo;
    } catch (error) {
      console.debug('Failed to read update info:', error);
      return null;
    }
  }

  private compareVersions(version1: string, version2: string): number {
    const v1Parts = version1.split('.').map(Number);
    const v2Parts = version2.split('.').map(Number);
    
    const maxLength = Math.max(v1Parts.length, v2Parts.length);
    
    for (let i = 0; i < maxLength; i++) {
      const v1Part = v1Parts[i] || 0;
      const v2Part = v2Parts[i] || 0;
      
      if (v1Part < v2Part) return -1;
      if (v1Part > v2Part) return 1;
    }
    
    return 0;
  }

  private async promptUserForUpdate(updateInfo: UpdateInfo): Promise<boolean> {
    console.log('\n' + '='.repeat(60));
    console.log('🚀 Intel Codex CLI Update Available!');
    console.log('='.repeat(60));
    console.log(`Current version: ${this.currentVersion}`);
    console.log(`Latest version:  ${updateInfo.version}`);
    console.log(`Release date:    ${updateInfo.releaseDate}`);
    
    if (updateInfo.changelog && updateInfo.changelog.length > 0) {
      console.log('\nWhat\'s new:');
      updateInfo.changelog.forEach(change => {
        console.log(`  • ${change}`);
      });
    }
    
    console.log('\n' + '='.repeat(60));
    
    if (updateInfo.required) {
      console.log('⚠️  This is a required update. Installing automatically...');
      return true;
    }
    
    console.log('Would you like to install this update now?');
    console.log('Press Y to install, N to skip, or S to skip and don\'t ask again for this version');
    
    return new Promise((resolve) => {
      process.stdin.setRawMode(true);
      process.stdin.resume();
      process.stdin.on('data', (key) => {
        const char = key.toString().toLowerCase();
        process.stdin.setRawMode(false);
        process.stdin.pause();
        
        if (char === 'y') {
          console.log('\nInstalling update...');
          resolve(true);
        } else if (char === 's') {
          console.log('\nSkipping this version...');
          this.saveSkippedVersion(updateInfo.version);
          resolve(false);
        } else {
          console.log('\nSkipping update...');
          resolve(false);
        }
      });
    });
  }

  private saveSkippedVersion(version: string): void {
    try {
      const configDir = path.join(os.homedir(), '.codex');
      if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
      }
      
      const skippedVersionsFile = path.join(configDir, 'skipped-versions.json');
      let skippedVersions: string[] = [];
      
      if (fs.existsSync(skippedVersionsFile)) {
        const content = fs.readFileSync(skippedVersionsFile, 'utf-8');
        skippedVersions = JSON.parse(content);
      }
      
      if (!skippedVersions.includes(version)) {
        skippedVersions.push(version);
        fs.writeFileSync(skippedVersionsFile, JSON.stringify(skippedVersions, null, 2));
      }
    } catch (error) {
      console.debug('Failed to save skipped version:', error);
    }
  }

  private isVersionSkipped(version: string): boolean {
    try {
      const configDir = path.join(os.homedir(), '.codex');
      const skippedVersionsFile = path.join(configDir, 'skipped-versions.json');
      
      if (!fs.existsSync(skippedVersionsFile)) {
        return false;
      }
      
      const content = fs.readFileSync(skippedVersionsFile, 'utf-8');
      const skippedVersions: string[] = JSON.parse(content);
      
      return skippedVersions.includes(version);
    } catch (error) {
      return false;
    }
  }

  private async downloadAndInstall(_updateInfo: UpdateInfo): Promise<boolean> {
    try {
      console.log('Downloading update...');
      
      const packagePath = path.join(this.networkShare, this.packageFile);
      if (!fs.existsSync(packagePath)) {
        console.error('Update package not found on network share');
        return false;
      }

      // Create temp directory for update
      const tempDir = path.join(os.tmpdir(), 'codex-update');
      if (fs.existsSync(tempDir)) {
        fs.rmSync(tempDir, { recursive: true, force: true });
      }
      fs.mkdirSync(tempDir, { recursive: true });

      // Copy update package to temp directory
      const tempPackagePath = path.join(tempDir, this.packageFile);
      fs.copyFileSync(packagePath, tempPackagePath);

      console.log('Extracting update...');
      
      // Extract the package (assuming it's a zip file)
      const extractDir = path.join(tempDir, 'extracted');
      
      // Use PowerShell to extract zip file
      const extractCommand = `powershell -Command "Expand-Archive -Path '${tempPackagePath}' -DestinationPath '${extractDir}' -Force"`;
      execSync(extractCommand, { stdio: 'pipe' });

      // Find the extracted intel-codex-cli-windows directory
      const extractedFiles = fs.readdirSync(extractDir);
      const codexDir = extractedFiles.find(file => 
        file.includes('intel-codex-cli-windows') && 
        fs.statSync(path.join(extractDir, file)).isDirectory()
      );

      if (!codexDir) {
        console.error('Could not find Codex CLI directory in update package');
        return false;
      }

      const codexPath = path.join(extractDir, codexDir);

      console.log('Installing update...');
      
      // Install the update globally
      const installCommand = `npm install -g "${codexPath}"`;
      execSync(installCommand, { stdio: 'inherit' });

      console.log('✅ Update installed successfully!');
      console.log('Please restart your terminal and run "codex --version" to verify the update.');
      
      // Clean up temp directory
      fs.rmSync(tempDir, { recursive: true, force: true });
      
      return true;
    } catch (error) {
      console.error('Failed to install update:', error);
      return false;
    }
  }

  public async checkForUpdates(): Promise<boolean> {
    try {
      // Check if network share is accessible
      const networkAccessible = await this.checkNetworkShareAccess();
      if (!networkAccessible) {
        // Silently fail - don't bother users with network issues
        return false;
      }

      // Get update information
      const updateInfo = await this.getUpdateInfo();
      if (!updateInfo) {
        // No update info available
        return false;
      }

      // Compare versions
      const versionComparison = this.compareVersions(this.currentVersion, updateInfo.version);
      if (versionComparison >= 0) {
        // Current version is up to date or newer
        return false;
      }

      // Check if user has skipped this version
      if (this.isVersionSkipped(updateInfo.version) && !updateInfo.required) {
        // User has skipped this version and it's not required
        return false;
      }

      // Prompt user for update
      const shouldUpdate = await this.promptUserForUpdate(updateInfo);
      if (!shouldUpdate) {
        if (updateInfo.required) {
          console.log('\n⚠️  This update is required. Codex CLI will exit.');
          process.exit(1);
        }
        return false;
      }

      // Download and install update
      const updateSuccess = await this.downloadAndInstall(updateInfo);
      if (updateSuccess && updateInfo.required) {
        console.log('\nUpdate completed. Please restart Codex CLI.');
        process.exit(0);
      }

      return updateSuccess;
    } catch (error) {
      // Silently fail - don't let update check break the CLI
      console.debug('Update check failed:', error);
      return false;
    }
  }

  public async checkForUpdatesQuiet(): Promise<{ updateAvailable: boolean; updateInfo?: UpdateInfo }> {
    try {
      const networkAccessible = await this.checkNetworkShareAccess();
      if (!networkAccessible) {
        return { updateAvailable: false };
      }

      const updateInfo = await this.getUpdateInfo();
      if (!updateInfo) {
        return { updateAvailable: false };
      }

      const versionComparison = this.compareVersions(this.currentVersion, updateInfo.version);
      const updateAvailable = versionComparison < 0;

      return { updateAvailable, updateInfo: updateAvailable ? updateInfo : undefined };
    } catch (error) {
      return { updateAvailable: false };
    }
  }
}

// Export singleton instance
export const updateManager = new UpdateManager();

// Function to check for updates on CLI startup
export async function checkForUpdatesOnStartup(): Promise<void> {
  await updateManager.checkForUpdates();
}
