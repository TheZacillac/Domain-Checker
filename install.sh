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
pip3 install -e .

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
    echo "  domain-check lookup example.com"
    echo "  domain-check bulk example.com google.com"
    echo "  domain-check interactive"
    echo "  python3 examples/basic_usage.py"
    echo ""
    echo "For more information, see README.md"
else
    echo "❌ Installation test failed"
    exit 1
fi
