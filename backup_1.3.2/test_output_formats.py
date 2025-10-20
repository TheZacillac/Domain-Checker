#!/usr/bin/env python3
"""
Test script to demonstrate the new output format features
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and display its output"""
    print(f"\n{'='*80}")
    print(f"Command: {cmd}")
    print('='*80)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    print('='*80)

def main():
    """Test various output formats"""
    
    print("\n" + "="*80)
    print("DOMAIN CHECKER - OUTPUT FORMAT TESTS")
    print("="*80)
    
    # Test 1: Single domain lookup with different formats
    print("\n\n### TEST 1: Single Domain Lookup ###")
    
    print("\n1a. Rich format (default):")
    run_command("domch lookup example.com")
    
    print("\n1b. Plain format (copy/paste friendly):")
    run_command("domch lookup example.com --format plain")
    
    print("\n1c. JSON format (programmatic use):")
    run_command("domch lookup example.com --format json")
    
    # Test 2: DIG lookup with different formats
    print("\n\n### TEST 2: DIG Lookup ###")
    
    print("\n2a. DIG with plain format:")
    run_command("domch dig example.com --record A --format plain")
    
    print("\n2b. DIG with JSON format:")
    run_command("domch dig example.com --record A --format json")
    
    # Test 3: Bulk lookup with different formats
    print("\n\n### TEST 3: Bulk Domain Lookup ###")
    
    print("\n3a. Bulk with plain format:")
    run_command("domch bulk example.com google.com --format plain")
    
    print("\n3b. Bulk with JSON format:")
    run_command("domch bulk example.com google.com --format json")
    
    print("\n3c. Bulk with CSV format (Excel-friendly):")
    run_command("domch bulk example.com google.com --format csv")
    
    # Test 4: Propagation check with different formats
    print("\n\n### TEST 4: DNS Propagation Check ###")
    
    print("\n4a. Propagation with plain format:")
    run_command("domch prop example.com --record A --format plain --timeout 5")
    
    print("\n4b. Propagation with JSON format:")
    run_command("domch prop example.com --record A --format json --timeout 5")
    
    print("\n\n" + "="*80)
    print("ALL TESTS COMPLETED!")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running tests: {e}")
        sys.exit(1)

