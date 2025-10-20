#!/bin/bash

# Quick installation script for Domain Checker
# Usage: curl -sSL https://raw.githubusercontent.com/your-repo/domain-checker/main/quick_install.sh | bash

set -e

echo "🚀 Quick Install: Domain Checker"

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [ "$(printf '%s\n' "3.8" "$python_version" | sort -V | head -n1)" != "3.8" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install aiohttp python-whois rich click pydantic typer mcp asyncio-throttle

# Install the package
echo "🔧 Installing domain checker..."

# Check if pipx is available and use it, otherwise fallback to pip3
if command -v pipx &> /dev/null; then
    echo "📦 Using pipx for isolated installation..."
    pipx install -e .
else
    echo "📦 Using pip3 for installation (with --break-system-packages)..."
    pip3 install -e . --break-system-packages
fi

# Test installation
echo "🧪 Testing installation..."
python3 -c "
import asyncio
from domain_checker import DomainChecker

async def test():
    checker = DomainChecker()
    result = await checker.lookup_domain('example.com')
    print(f'✅ Test successful: {result.domain} -> {result.data.registrar if result.data else \"No data\"}')

asyncio.run(test())
"

echo ""
echo "✅ Domain Checker installed successfully!"
echo ""
echo "Usage:"
echo "  domch lookup example.com"
echo "  domch bulk example.com google.com"
echo "  domch interactive"
echo ""
echo "For Rust extensions (optional):"
echo "  1. Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
echo "  2. Run: python3 build.py"
echo ""
