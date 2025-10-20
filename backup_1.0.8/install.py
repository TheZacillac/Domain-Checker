#!/usr/bin/env python3
"""
Cross-platform installation script for Domain Checker
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ is required. Found: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_rust():
    """Check if Rust is installed"""
    success, stdout, stderr = run_command("rustc --version", check=False)
    if success:
        print(f"✅ Rust found: {stdout.strip()}")
        return True
    else:
        print("⚠️  Rust not found - will use Python-only implementation")
        return False


def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Try pip first, then pip3
    pip_cmd = "pip" if shutil.which("pip") else "pip3"
    
    success, stdout, stderr = run_command(f"{pip_cmd} install -r requirements.txt")
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    print("✅ Python dependencies installed")
    return True


def install_package():
    """Install the domain checker package"""
    print("🔧 Installing domain checker...")
    
    # Try pipx first, then fallback to pip/pip3
    if shutil.which("pipx"):
        install_cmd = "pipx install -e ."
        print("📦 Using pipx for isolated installation...")
    else:
        pip_cmd = "pip" if shutil.which("pip") else "pip3"
        install_cmd = f"{pip_cmd} install -e . --break-system-packages"
        print("📦 Using pip for installation (with --break-system-packages)...")
    
    success, stdout, stderr = run_command(install_cmd)
    if not success:
        print(f"❌ Failed to install package: {stderr}")
        return False
    
    print("✅ Domain checker installed")
    return True


def build_rust_extensions():
    """Build Rust extensions if Rust is available"""
    if not check_rust():
        return True
    
    print("🦀 Building Rust extensions...")
    
    # Check if Cargo.toml exists
    if not Path("Cargo.toml").exists():
        print("⚠️  No Cargo.toml found - skipping Rust build")
        return True
    
    success, stdout, stderr = run_command("cargo build --release")
    if not success:
        print(f"⚠️  Rust build failed: {stderr}")
        print("   Continuing with Python-only implementation...")
        return True
    
    print("✅ Rust extensions built")
    return True


def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    
    success, stdout, stderr = run_command("python3 test_domain_checker.py")
    if not success:
        print(f"❌ Installation test failed: {stderr}")
        return False
    
    print("✅ Installation test passed")
    return True


def create_aliases():
    """Create convenient aliases"""
    print("🔗 Creating aliases...")
    
    shell_configs = []
    if platform.system() == "Darwin":  # macOS
        shell_configs = ["~/.zshrc", "~/.bash_profile"]
    else:  # Linux
        shell_configs = ["~/.bashrc", "~/.zshrc"]
    
    aliases = [
        "alias dc='domch'",
        "alias domain-checker='domch'",
    ]
    
    for config_file in shell_configs:
        config_path = Path(config_file).expanduser()
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                
                # Add aliases if not already present
                new_aliases = []
                for alias in aliases:
                    if alias not in content:
                        new_aliases.append(alias)
                
                if new_aliases:
                    with open(config_path, 'a') as f:
                        f.write("\n# Domain Checker aliases\n")
                        for alias in new_aliases:
                            f.write(f"{alias}\n")
                    
                    print(f"✅ Added aliases to {config_file}")
            except Exception as e:
                print(f"⚠️  Could not update {config_file}: {e}")
    
    return True


def main():
    """Main installation function"""
    print("🚀 Domain Checker Installation")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check Rust
    has_rust = check_rust()
    
    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    # Build Rust extensions if available
    if not build_rust_extensions():
        sys.exit(1)
    
    # Install package
    if not install_package():
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        sys.exit(1)
    
    # Create aliases
    create_aliases()
    
    print("\n" + "=" * 40)
    print("✅ Domain Checker installed successfully!")
    print("\nUsage examples:")
    print("  domch lookup example.com")
    print("  domch bulk example.com google.com")
    print("  domch interactive")
    print("  dc lookup example.com  # (if aliases were created)")
    print("\nFor more information, see README.md")
    
    if has_rust:
        print("\n🦀 Rust extensions are available for enhanced performance!")
    else:
        print("\n💡 Install Rust for enhanced performance: https://rustup.rs/")


if __name__ == "__main__":
    main()
