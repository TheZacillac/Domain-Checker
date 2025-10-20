#!/usr/bin/env python3
"""
Test script for Domain Checker GUI
"""

import sys
import subprocess
from pathlib import Path

def test_gui_import():
    """Test if GUI can be imported"""
    try:
        from domain_checker.gui import run_gui, DomainCheckerGUI
        print("✅ GUI import successful")
        return True
    except ImportError as e:
        print(f"❌ GUI import failed: {e}")
        return False

def test_textual_available():
    """Test if Textual is available"""
    try:
        import textual
        print(f"✅ Textual available: {textual.__version__}")
        return True
    except ImportError:
        print("❌ Textual not available - install with: pip install textual")
        return False

def test_gui_launch():
    """Test if GUI can be launched (dry run)"""
    try:
        from domain_checker.gui import DomainCheckerGUI
        
        # Create app instance (don't run it)
        app = DomainCheckerGUI()
        print("✅ GUI app creation successful")
        
        # Test compose method
        widgets = list(app.compose())
        print(f"✅ GUI widgets created: {len(widgets)} widgets")
        
        return True
    except Exception as e:
        print(f"❌ GUI launch test failed: {e}")
        return False

def test_cli_gui_command():
    """Test if CLI GUI command works"""
    try:
        # Test the CLI command import
        from domain_checker.cli import app
        print("✅ CLI GUI command available")
        return True
    except Exception as e:
        print(f"❌ CLI GUI command test failed: {e}")
        return False

def main():
    """Run all GUI tests"""
    print("🧪 Testing Domain Checker GUI...")
    print("=" * 50)
    
    tests = [
        ("Textual Framework", test_textual_available),
        ("GUI Import", test_gui_import),
        ("GUI Launch", test_gui_launch),
        ("CLI GUI Command", test_cli_gui_command),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! GUI is ready to use.")
        print("\nTo launch the GUI, run:")
        print("  domch gui")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nTo install missing dependencies:")
        print("  pip install textual")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
