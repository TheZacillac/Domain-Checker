# GUI Installation Guide

## The Issue
When you install Domain Checker with `pipx`, it creates an isolated environment. If you then install `textual` separately with `pipx`, it goes into a different isolated environment and isn't available to Domain Checker.

## The Solution

### For pipx Users (Recommended)
If you installed Domain Checker with `pipx`, use `pipx inject` to add the GUI dependency:

```bash
pipx inject domain-checker textual
```

This adds `textual` to the same isolated environment as Domain Checker.

### For pip Users
If you installed Domain Checker with `pip`, install textual normally:

```bash
pip install textual
```

## Step-by-Step Instructions

### 1. Check Your Installation Method
```bash
# Check if you have domch installed
domch --version

# If that works, you have Domain Checker installed
```

### 2. Install GUI Dependency

**If you used pipx to install Domain Checker:**
```bash
pipx inject domain-checker textual
```

**If you used pip to install Domain Checker:**
```bash
pip install textual
```

### 3. Launch the GUI
```bash
domch gui
```

## Troubleshooting

### Error: "No module named 'textual'"
This means textual isn't installed in the same environment as Domain Checker.

**Solution:**
```bash
# For pipx installations:
pipx inject domain-checker textual

# For pip installations:
pip install textual
```

### Error: "pipx inject command not found"
Make sure you have the latest version of pipx:
```bash
pip install --upgrade pipx
```

### Still Having Issues?
Try reinstalling Domain Checker with all dependencies:
```bash
# Uninstall first
pipx uninstall domain-checker

# Reinstall with dependencies
pipx install domain-checker[gui]
```

## Why This Happens

### pipx Isolation
- `pipx` creates isolated environments for each package
- Each package gets its own Python environment
- Dependencies installed separately don't share environments

### pipx inject
- `pipx inject` adds packages to an existing pipx environment
- This is the correct way to add dependencies to pipx-installed packages
- It ensures the dependency is available to the main package

## Alternative: Install Everything Together

If you want to avoid the injection step, you can install Domain Checker with all dependencies:

```bash
# Clone the repository
git clone https://github.com/TheZacillac/domain-checker.git
cd domain-checker

# Install with pipx (includes all dependencies)
pipx install -e .
```

This installs Domain Checker in development mode with all dependencies from `requirements.txt`.

## Verification

After installing textual, verify it works:

```bash
# Test the GUI command
domch gui

# If it launches the GUI, you're all set!
# Press Ctrl+C or Q to exit the GUI
```

## Summary

The key command for most users:
```bash
pipx inject domain-checker textual
```

This adds the GUI dependency to your existing Domain Checker installation, allowing you to use `domch gui` to launch the user-friendly interface.
