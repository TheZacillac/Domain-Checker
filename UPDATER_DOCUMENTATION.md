# Domain Checker Updater

## Overview
The Domain Checker includes a comprehensive updater system that can check for updates from the repository and automatically update the installation. The updater supports both CLI integration and standalone operation.

## Features

### 🔍 Update Checking
- Checks for latest releases from GitHub
- Falls back to latest commits from main branch
- Compares versions using semantic versioning
- Shows release notes and commit messages

### 📦 Automatic Updates
- Downloads latest code from repository
- Creates automatic backups before updating
- Preserves configuration and data files
- Handles file conflicts gracefully

### 🔄 Rollback Support
- Creates versioned backups
- Allows rollback to previous versions
- Preserves multiple backup versions

### 🛡️ Safety Features
- Automatic backup creation
- Confirmation prompts for updates
- SSL certificate handling
- Error recovery and reporting

## Usage

### CLI Integration

#### Check for Updates
```bash
domain-check update --check
```
Shows if updates are available without installing them.

#### Update Installation
```bash
domain-check update
```
Checks for updates and prompts to install if available.

#### Force Update
```bash
domain-check update --force
```
Forces update even if no changes are detected.

#### Rollback to Previous Version
```bash
domain-check update --rollback 1.0.4
```
Rolls back to a specific version using backup.

### Standalone Updater

#### Run Standalone Script
```bash
python3 update.py
```
Runs the standalone updater with interactive prompts.

### Python API

#### Check for Updates
```python
from domain_checker.updater import DomainCheckerUpdater

updater = DomainCheckerUpdater()
has_updates, latest_version, update_info = await updater.check_for_updates()

if has_updates:
    print(f"Update available: {latest_version}")
else:
    print("You're running the latest version!")
```

#### Update Installation
```python
from domain_checker.updater import DomainCheckerUpdater

updater = DomainCheckerUpdater()
success = await updater.update_installation()

if success:
    print("Update completed successfully!")
else:
    print("Update failed!")
```

#### Quick Update Check
```python
from domain_checker.update_checker import quick_check

message = await quick_check()
print(message)
```

## Configuration

### Updater Configuration File
The updater uses `updater_config.json` for configuration:

```json
{
  "repository": {
    "url": "https://github.com/TheZacillac/domain-checker.git",
    "branch": "main",
    "api_url": "https://api.github.com/repos/TheZacillac/domain-checker"
  },
  "update": {
    "auto_backup": true,
    "backup_retention": 3,
    "exclude_patterns": [
      ".git",
      "__pycache__",
      "*.pyc",
      "backup_*",
      ".DS_Store",
      "*.log"
    ],
    "require_confirmation": true
  },
  "notifications": {
    "check_on_startup": false,
    "show_release_notes": true,
    "show_commit_messages": true
  }
}
```

### Configuration Options

#### Repository Settings
- `url`: Git repository URL
- `branch`: Branch to track for updates
- `api_url`: GitHub API URL for release information

#### Update Settings
- `auto_backup`: Automatically create backups before updates
- `backup_retention`: Number of backup versions to keep
- `exclude_patterns`: Files/patterns to exclude from updates
- `require_confirmation`: Require user confirmation before updates

#### Notification Settings
- `check_on_startup`: Check for updates when CLI starts
- `show_release_notes`: Display release notes in update notifications
- `show_commit_messages`: Display commit messages for main branch updates

## Update Process

### 1. Update Check
1. Connects to GitHub API
2. Fetches latest release information
3. Compares with current version
4. Shows update information if available

### 2. Update Installation
1. Creates backup of current installation
2. Clones latest repository to temporary directory
3. Copies updated files to installation directory
4. Preserves configuration and data files
5. Cleans up temporary files

### 3. Backup Management
- Backups are stored in `backup_{version}` directories
- Multiple backup versions are preserved
- Old backups can be cleaned up automatically

## File Handling

### Files Updated
- Python source files (`.py`)
- Configuration files (`.json`, `.toml`)
- Documentation files (`.md`)
- Scripts and utilities

### Files Preserved
- User configuration files
- Data directories
- Log files
- Backup directories

### Excluded Files
- Git repository (`.git`)
- Python cache (`__pycache__`, `*.pyc`)
- Backup directories (`backup_*`)
- System files (`.DS_Store`)
- Log files (`*.log`)

## Error Handling

### Network Issues
- SSL certificate verification bypass
- Connection timeout handling
- API rate limit handling

### File System Issues
- Permission error handling
- Disk space checking
- File conflict resolution

### Update Failures
- Automatic rollback on failure
- Detailed error reporting
- Recovery instructions

## Security Considerations

### SSL/TLS
- Bypasses SSL certificate verification for compatibility
- Uses secure HTTPS connections
- Handles certificate chain issues

### Code Integrity
- Downloads from official repository
- Preserves file permissions
- Validates file operations

### Backup Security
- Creates secure backups before updates
- Preserves user data and configurations
- Allows safe rollback

## Troubleshooting

### Common Issues

#### SSL Certificate Errors
```
Error: [SSL: CERTIFICATE_VERIFY_FAILED]
```
**Solution**: The updater automatically handles SSL issues by bypassing certificate verification.

#### Permission Errors
```
Error: Permission denied
```
**Solution**: Run with appropriate permissions or use `sudo` if necessary.

#### Network Connectivity
```
Error: Cannot connect to host
```
**Solution**: Check internet connection and firewall settings.

#### Git Not Found
```
Error: git command not found
```
**Solution**: Install Git or use the standalone updater script.

### Recovery Procedures

#### Failed Update
1. Check error messages for specific issues
2. Use rollback feature to restore previous version
3. Check network connectivity and permissions
4. Try force update if needed

#### Corrupted Installation
1. Use rollback to restore from backup
2. Reinstall from scratch if backups are unavailable
3. Check file permissions and disk space

## Examples

### Basic Update Workflow
```bash
# Check for updates
domain-check update --check

# Update if available
domain-check update

# Rollback if needed
domain-check update --rollback 1.0.4
```

### Automated Update Script
```python
import asyncio
from domain_checker.updater import DomainCheckerUpdater

async def auto_update():
    updater = DomainCheckerUpdater()
    has_updates, _, _ = await updater.check_for_updates()
    
    if has_updates:
        print("Updates available, installing...")
        success = await updater.update_installation(force=True)
        if success:
            print("Update completed successfully!")
        else:
            print("Update failed!")

asyncio.run(auto_update())
```

### Integration with CI/CD
```bash
#!/bin/bash
# Update script for CI/CD pipeline

# Check for updates
if domain-check update --check | grep -q "Update available"; then
    echo "Updates found, installing..."
    domain-check update --force
    echo "Update completed"
else
    echo "No updates available"
fi
```

## Best Practices

### Regular Updates
- Check for updates regularly
- Keep backups of important configurations
- Test updates in development environment first

### Backup Management
- Monitor backup disk usage
- Clean up old backups periodically
- Verify backup integrity

### Security
- Review update sources
- Validate update integrity
- Keep system updated

The Domain Checker updater provides a robust, safe, and user-friendly way to keep your installation current with the latest features and improvements! 🚀
