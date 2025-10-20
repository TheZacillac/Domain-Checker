#!/bin/bash

# Domain Checker Installation Script

echo "🚀 Installing Domain Checker..."

# Check if Python 3.8+ is installed
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

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

if [ $? -ne 0 ]; then
    echo "❌ Failed to install domain checker"
    exit 1
fi

# Test installation
echo "🧪 Testing installation..."
python3 test_domain_checker.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Domain Checker installed successfully!"
    echo ""
    echo "Usage examples:"
    echo "  domch lookup example.com"
    echo "  domch bulk example.com google.com"
    echo "  domch interactive"
    echo "  python3 examples/basic_usage.py"
    echo ""
    echo "For more information, see README.md"
else
    echo "❌ Installation test failed"
    exit 1
fi
