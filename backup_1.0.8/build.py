#!/usr/bin/env python3
"""
Build script for domain checker with optional Rust extensions
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_rust():
    """Check if Rust is installed"""
    success, stdout, stderr = run_command("rustc --version", check=False)
    return success


def build_rust_extensions():
    """Build Rust extensions"""
    if not check_rust():
        print("❌ Rust not found. Install Rust from https://rustup.rs/")
        return False
    
    print("🦀 Building Rust extensions...")
    
    # Build the Rust extension
    success, stdout, stderr = run_command("cargo build --release")
    if not success:
        print(f"❌ Rust build failed: {stderr}")
        return False
    
    print("✅ Rust extensions built successfully")
    return True


def create_python_bindings():
    """Create Python bindings for Rust extensions"""
    if not Path("target/release/libdomain_checker_rust.so").exists() and not Path("target/release/libdomain_checker_rust.dylib").exists():
        print("❌ Rust extension not found. Build failed.")
        return False
    
    # Create Python module that imports Rust extensions
    rust_module = '''
"""
Rust extensions for domain checker
"""

try:
    from .domain_checker_rust import RdapClient, rust_validate_domain, rust_lookup_domain
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    RdapClient = None
    rust_validate_domain = None
    rust_lookup_domain = None

def is_rust_available():
    """Check if Rust extensions are available"""
    return RUST_AVAILABLE

def get_rust_rdap_client(timeout_secs=30):
    """Get Rust RDAP client if available"""
    if RUST_AVAILABLE:
        return RdapClient(timeout_secs)
    return None

def validate_domain_rust(domain):
    """Validate domain using Rust if available"""
    if RUST_AVAILABLE:
        return rust_validate_domain(domain)
    return None

def lookup_domain_rust(domain, timeout_secs=30):
    """Lookup domain using Rust if available"""
    if RUST_AVAILABLE:
        return rust_lookup_domain(domain, timeout_secs)
    return None
'''
    
    with open("domain_checker/rust_extensions.py", "w") as f:
        f.write(rust_module)
    
    print("✅ Python bindings created")
    return True


def main():
    """Main build function"""
    print("🔨 Building Domain Checker...")
    
    if check_rust():
        print("✅ Rust found")
        if build_rust_extensions():
            create_python_bindings()
            print("🦀 Rust extensions built and integrated")
        else:
            print("⚠️  Rust build failed, using Python-only implementation")
    else:
        print("⚠️  Rust not found, using Python-only implementation")
    
    print("✅ Build completed")


if __name__ == "__main__":
    main()
