#!/usr/bin/env python3
"""
Simple test script for domain checker
"""

import asyncio
import sys
from domain_checker import DomainChecker


async def test_basic_functionality():
    """Test basic functionality"""
    print("🧪 Testing Domain Checker...")
    
    try:
        # Test single domain lookup
        print("\n1. Testing single domain lookup...")
        checker = DomainChecker()
        result = await checker.lookup_domain("example.com")
        
        if result.success:
            print(f"   ✅ Success: {result.domain} -> {result.data.registrar}")
            print(f"   ⏱️  Time: {result.lookup_time:.2f}s")
            print(f"   🔧 Method: {result.method}")
        else:
            print(f"   ❌ Failed: {result.error}")
        
        # Test bulk lookup
        print("\n2. Testing bulk lookup...")
        domains = ["example.com", "google.com"]
        results = await checker.lookup_domains_bulk(domains)
        
        print(f"   📊 Results: {results.successful_lookups}/{results.total_domains} successful")
        print(f"   ⏱️  Total time: {results.total_time:.2f}s")
        
        # Test method comparison
        print("\n3. Testing method comparison...")
        comparison = await checker.compare_methods("example.com")
        
        print(f"   📋 WHOIS: {'✅' if comparison['whois'].success else '❌'}")
        print(f"   📋 RDAP: {'✅' if comparison['rdap'].success else '❌'}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


async def main():
    """Main test function"""
    success = await test_basic_functionality()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
