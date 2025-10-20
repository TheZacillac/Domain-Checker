#!/usr/bin/env python3
"""
DIG examples for domain checker
"""

import asyncio
from domain_checker import DomainChecker


async def dig_examples():
    """Examples of DIG functionality"""
    print("🔍 DIG Examples for Domain Checker\n")
    
    checker = DomainChecker()
    
    # Example 1: Basic DIG lookup
    print("=== Example 1: Basic DIG Lookup ===")
    result = await checker.dig_lookup("example.com", "A")
    print(f"✅ A Records for example.com:")
    print(f"   Raw Data: {result.data.raw_data}")
    print(f"   Lookup Time: {result.lookup_time:.2f}s")
    
    # Example 2: Different record types
    print("\n=== Example 2: Different Record Types ===")
    record_types = ["A", "AAAA", "MX", "NS", "TXT", "SOA"]
    
    for record_type in record_types:
        result = await checker.dig_lookup("example.com", record_type)
        if result.success and result.data.raw_data:
            print(f"✅ {record_type} Records:")
            print(f"   {result.data.raw_data.strip()}")
        else:
            print(f"❌ {record_type} Records: No data or error")
    
    # Example 3: Reverse DNS lookup
    print("\n=== Example 3: Reverse DNS Lookup ===")
    ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
    
    for ip in ips:
        result = await checker.reverse_lookup(ip)
        if result.success and result.data:
            print(f"✅ {ip} -> {result.data.domain}")
        else:
            print(f"❌ {ip} -> Error: {result.error}")
    
    # Example 4: Bulk DIG lookups
    print("\n=== Example 4: Bulk DIG Lookups ===")
    domains = ["example.com", "google.com", "github.com"]
    results = await checker.lookup_domains_bulk(domains, "dig", "A")
    
    print(f"📊 Bulk DIG Results:")
    print(f"   Total: {results.total_domains}")
    print(f"   Successful: {results.successful_lookups}")
    print(f"   Failed: {results.failed_lookups}")
    print(f"   Total Time: {results.total_time:.2f}s")
    
    for result in results.results:
        if result.success:
            print(f"   ✅ {result.domain}: {result.data.raw_data.strip()}")
        else:
            print(f"   ❌ {result.domain}: {result.error}")
    
    # Example 5: Multiple record types for same domain
    print("\n=== Example 5: Multiple Record Types for Same Domain ===")
    domain = "google.com"
    record_types = ["A", "AAAA", "MX", "NS"]
    
    for record_type in record_types:
        result = await checker.dig_lookup(domain, record_type)
        if result.success and result.data.raw_data:
            print(f"✅ {domain} {record_type}: {result.data.raw_data.strip()}")
        else:
            print(f"❌ {domain} {record_type}: No data")
    
    # Example 6: Error handling
    print("\n=== Example 6: Error Handling ===")
    
    # Test with invalid domain
    result = await checker.dig_lookup("nonexistent-domain-12345.com", "A")
    if not result.success:
        print(f"❌ Expected failure for invalid domain: {result.error}")
    else:
        print(f"✅ Unexpected success for invalid domain")
    
    # Test with invalid record type
    result = await checker.dig_lookup("example.com", "INVALID")
    if not result.success:
        print(f"❌ Expected failure for invalid record type: {result.error}")
    else:
        print(f"✅ Unexpected success for invalid record type")
    
    print("\n✅ All DIG examples completed!")


async def dig_performance_test():
    """Test DIG performance vs other methods"""
    print("\n🚀 DIG Performance Test\n")
    
    checker = DomainChecker()
    domain = "example.com"
    
    # Test different methods
    methods = ["dig", "whois", "rdap"]
    results = {}
    
    for method in methods:
        if method == "dig":
            result = await checker.lookup_domain(domain, method, "A")
        else:
            result = await checker.lookup_domain(domain, method)
        
        results[method] = result
        print(f"📊 {method.upper()}: {result.lookup_time:.2f}s")
    
    # Find fastest method
    fastest = min(results.items(), key=lambda x: x[1].lookup_time)
    print(f"\n🏆 Fastest method: {fastest[0].upper()} ({fastest[1].lookup_time:.2f}s)")


async def dig_use_cases():
    """Common DIG use cases"""
    print("\n💡 Common DIG Use Cases\n")
    
    checker = DomainChecker()
    
    # Use case 1: Check if domain resolves
    print("=== Use Case 1: Check if Domain Resolves ===")
    domains = ["example.com", "google.com", "nonexistent-domain-12345.com"]
    
    for domain in domains:
        result = await checker.dig_lookup(domain, "A")
        if result.success and result.data.raw_data.strip():
            print(f"✅ {domain}: Resolves to {result.data.raw_data.strip()}")
        else:
            print(f"❌ {domain}: Does not resolve")
    
    # Use case 2: Get mail servers
    print("\n=== Use Case 2: Get Mail Servers ===")
    domains = ["gmail.com", "outlook.com", "yahoo.com"]
    
    for domain in domains:
        result = await checker.dig_lookup(domain, "MX")
        if result.success and result.data.raw_data.strip():
            print(f"✅ {domain} MX: {result.data.raw_data.strip()}")
        else:
            print(f"❌ {domain} MX: No mail servers")
    
    # Use case 3: Check name servers
    print("\n=== Use Case 3: Check Name Servers ===")
    domains = ["example.com", "google.com", "github.com"]
    
    for domain in domains:
        result = await checker.dig_lookup(domain, "NS")
        if result.success and result.data.raw_data.strip():
            print(f"✅ {domain} NS: {result.data.raw_data.strip()}")
        else:
            print(f"❌ {domain} NS: No name servers")
    
    # Use case 4: IPv6 support check
    print("\n=== Use Case 4: IPv6 Support Check ===")
    domains = ["google.com", "github.com", "example.com"]
    
    for domain in domains:
        result = await checker.dig_lookup(domain, "AAAA")
        if result.success and result.data.raw_data.strip():
            print(f"✅ {domain}: IPv6 enabled")
        else:
            print(f"❌ {domain}: No IPv6 support")


async def main():
    """Run all DIG examples"""
    try:
        await dig_examples()
        await dig_performance_test()
        await dig_use_cases()
        
        print("\n🎉 All DIG examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running DIG examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())
