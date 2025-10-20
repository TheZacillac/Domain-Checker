# Updater Fix Summary

## Problem
The `domch update --force` command was not pulling the latest files from GitHub, even when forced. Users would push changes to the repository but the updater wouldn't retrieve them.

## Root Causes Identified

1. **Version Check Logic Issue**: If your local version (e.g., 1.3.1) was newer than any GitHub release, the updater would think you're already on the latest version
2. **No Explicit Main Branch Targeting**: The clone command didn't explicitly target the main branch
3. **Missing Force Fetch**: Even with `--depth 1`, there was no guarantee of getting the absolute latest commit
4. **No Verification**: Users couldn't see which commit was actually pulled

## Fixes Applied

### 1. Force Update Bypass
**Before:**
```python
has_updates, latest_version, update_info = await self.check_for_updates()

if not has_updates and not force:
    console.print("[green]✅ You're already running the latest version![/green]")
    return True
```

**After:**
```python
if force:
    console.print("[yellow]⚡ Force update requested - pulling latest from main branch...[/yellow]")
    has_updates = True
    latest_version = "main (latest)"
    update_info = {"source": "forced"}
else:
    has_updates, latest_version, update_info = await self.check_for_updates()
    
    if not has_updates:
        console.print("[green]✅ You're already running the latest version![/green]")
        console.print("[dim]Use --force to update anyway[/dim]")
        return True
```

**Benefit:** Force flag now completely bypasses version checking

### 2. Explicit Main Branch Targeting
**Before:**
```python
result = subprocess.run([
    "git", "clone", "--depth", "1", 
    self.repo_url, self.temp_dir
], capture_output=True, text=True)
```

**After:**
```python
clone_cmd = [
    "git", "clone",
    "--depth", "1",
    "--branch", "main",
    "--single-branch",
    self.repo_url,
    self.temp_dir
]

result = subprocess.run(
    clone_cmd,
    capture_output=True,
    text=True,
    env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
)
```

**Benefit:** Explicitly targets main branch, no ambiguity

### 3. Force Fetch and Reset
**New Addition:**
```python
if force:
    # Fetch to ensure we have the very latest
    fetch_result = subprocess.run(
        ["git", "fetch", "origin", "main"],
        cwd=self.temp_dir,
        capture_output=True,
        text=True
    )
    if fetch_result.returncode == 0:
        # Reset to latest
        subprocess.run(
            ["git", "reset", "--hard", "origin/main"],
            cwd=self.temp_dir,
            capture_output=True,
            text=True
        )
```

**Benefit:** When force is used, performs additional fetch/reset to guarantee latest commit

### 4. Commit Hash Verification
**New Addition:**
```python
# Get the commit hash that was pulled
commit_result = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    cwd=self.temp_dir,
    capture_output=True,
    text=True
)
if commit_result.returncode == 0:
    commit_hash = commit_result.stdout.strip()[:8]

# Get commit message and date
# ... (additional git log commands)

# Store for display
self.pulled_commit_hash = commit_hash
self.pulled_commit_msg = commit_msg
self.pulled_commit_date = commit_date
```

**Benefit:** Users can now verify exactly which commit was pulled

### 5. Enhanced Results Display
**New Addition:**
```python
# Add commit information if available
if hasattr(self, 'pulled_commit_hash') and self.pulled_commit_hash:
    result_text += f"\n[bold cyan]📦 Pulled Commit:[/bold cyan]\n"
    result_text += f"  [bold]Hash:[/bold] {self.pulled_commit_hash}\n"
    if self.pulled_commit_msg:
        result_text += f"  [bold]Message:[/bold] {msg_preview}\n"
    if self.pulled_commit_date:
        result_text += f"  [bold]Date:[/bold] {self.pulled_commit_date}\n"
```

**Benefit:** Clear feedback showing what was pulled

## New Behavior

### Normal Update (without --force)
```bash
domch update
```

**Flow:**
1. Checks GitHub releases for version comparison
2. If no release, checks main branch commits
3. Compares version numbers
4. If up to date, shows message: "Use --force to update anyway"
5. If update available, prompts for confirmation

### Force Update (with --force)
```bash
domch update --force
```

**Flow:**
1. Skips version checking entirely
2. Shows force update warning
3. Clones from main branch with `--single-branch`
4. Performs git fetch + reset to ensure absolute latest
5. Shows which commit was pulled (hash, message, date)
6. Updates all files
7. Auto-reinstalls if Python files changed

## How to Verify

After running `domch update --force`, you'll see:

```
⚡ Force update requested - pulling latest from main branch...

┌─ Force Update ──────────────────────────┐
│ Current Version: 1.3.1                  │
│ Target: Latest main branch              │
│                                         │
│ This will pull the absolute latest     │
│ code from GitHub.                       │
└─────────────────────────────────────────┘

[Updating files...]

┌─ Update Results ────────────────────────┐
│ Update Complete!                        │
│                                         │
│ Files Updated: 15                       │
│ Files Skipped: 5                        │
│ Backup Location: /path/to/backup       │
│                                         │
│ 📦 Pulled Commit:                       │
│   Hash: a1b2c3d4                        │
│   Message: Add output format support    │
│   Date: 2025-01-27 14:30:25 -0500      │
│                                         │
│ Updated Files:                          │
│   • domain_checker/cli.py               │
│   • domain_checker/updater.py           │
│   • README.md                           │
│   ... and 12 more files                 │
└─────────────────────────────────────────┘
```

## Testing

To test the fix:

1. **Make a change to a file on GitHub** (e.g., add a comment)
2. **Wait a moment** for GitHub to process the commit
3. **Run force update:**
   ```bash
   domch update --force
   ```
4. **Verify the commit hash** shown matches the latest commit on GitHub
5. **Check the file** was actually updated with your change

## Comparison: Before vs After

| Scenario | Before | After |
|----------|--------|-------|
| Local version > GitHub release | ✅ "Already latest" | ✅ Can force update |
| Local version = GitHub release | ✅ "Already latest" | ✅ Can force update |
| Force flag used | ❌ Still checked versions | ✅ Bypasses checks |
| Commit verification | ❌ No way to verify | ✅ Shows hash/msg/date |
| Main branch targeting | ⚠️ Implicit | ✅ Explicit |
| Fetch latest when forced | ❌ No | ✅ Yes |

## Files Modified

1. `domain_checker/updater.py` - Main updater logic
2. `CHANGELOG.md` - Version 1.3.1 entry
3. `domain_checker/__init__.py` - Version bump to 1.3.1
4. `pyproject.toml` - Version bump to 1.3.1

## Summary

The updater now properly handles force updates by:
- Completely bypassing version checks when `--force` is used
- Explicitly targeting the main branch
- Performing additional fetch/reset to guarantee latest code
- Showing commit verification (hash, message, date)
- Providing clear feedback about what was pulled

Users can now confidently run `domch update --force` to get the absolute latest code from GitHub, and they'll see exactly which commit was pulled for verification.

