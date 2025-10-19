#!/usr/bin/env python3
"""
Basic usage examples for domain checker
"""

import asyncio
import json
from domain_checker import DomainChecker


async def single_domain_lookup():
    """Example: Lookup a single domain"""
    print("=== Single Domain Lookup ===")
    
    checker = DomainChecker()
    result = await checker.lookup_domain("example.com")
    
    if result.success:
        print(f"✅ Domain: {result.data.domain}")
        print(f"📋 Registrar: {result.data.registrar}")
        print(f"📅 Creation: {result.data.creation_date}")
        print(f"⏰ Expiration: {result.data.expiration_date}")
        print(f"🔄 Last Updated: {result.data.updated_date}")
        print(f"📊 Status: {', '.join(result.data.status)}")
        print(f"🌐 Name Servers: {', '.join(result.data.name_servers)}")
        print(f"⏱️  Lookup Time: {result.lookup_time:.2f}s")
        print(f"🔧 Method: {result.method}")
    else:
        print(f"❌ Error: {result.error}")


async def bulk_domain_lookup():
    """Example: Bulk domain lookup"""
    print("\n=== Bulk Domain Lookup ===")
    
    checker = DomainChecker(max_concurrent=5, rate_limit=2.0)
    
    domains = [
        "example.com",
        "google.com",
        "github.com",
        "stackoverflow.com",
        "reddit.com"
    ]
    
    results = await checker.lookup_domains_bulk(domains)
    
    print(f"📊 Summary:")
    print(f"   Total: {results.total_domains}")
    print(f"   Successful: {results.successful_lookups}")
    print(f"   Failed: {results.failed_lookups}")
    print(f"   Total Time: {results.total_time:.2f}s")
    print(f"   Average Time: {results.average_time_per_domain:.2f}s")
    
    print(f"\n📋 Results:")
    for result in results.results:
        if result.success:
            print(f"   ✅ {result.domain}: {result.data.registrar} ({result.method})")
        else:
            print(f"   ❌ {result.domain}: {result.error}")


async def method_comparison():
    """Example: Compare WHOIS vs RDAP"""
    print("\n=== Method Comparison ===")
    
    checker = DomainChecker()
    comparison = await checker.compare_methods("example.com")
    
    print(f"🔍 Comparing methods for: {comparison['domain']}")
    
    # WHOIS results
    whois_result = comparison['whois']
    print(f"\n📋 WHOIS:")
    print(f"   Success: {'✅' if whois_result.success else '❌'}")
    print(f"   Time: {whois_result.lookup_time:.2f}s")
    if whois_result.success and whois_result.data:
        print(f"   Registrar: {whois_result.data.registrar}")
    
    # RDAP results
    rdap_result = comparison['rdap']
    print(f"\n📋 RDAP:")
    print(f"   Success: {'✅' if rdap_result.success else '❌'}")
    print(f"   Time: {rdap_result.lookup_time:.2f}s")
    if rdap_result.success and rdap_result.data:
        print(f"   Registrar: {rdap_result.data.registrar}")
    
    # Comparison summary
    comp = comparison['comparison']
    print(f"\n📊 Comparison Summary:")
    print(f"   WHOIS Success: {'✅' if comp['whois_success'] else '❌'}")
    print(f"   RDAP Success: {'✅' if comp['rdap_success'] else '❌'}")
    print(f"   WHOIS Time: {comp['whois_time']:.2f}s")
    print(f"   RDAP Time: {comp['rdap_time']:.2f}s")


async def file_processing():
    """Example: Process domains from file"""
    print("\n=== File Processing ===")
    
    # Create a sample domains file
    sample_domains = [
        "example.com",
        "google.com",
        "github.com",
        "stackoverflow.com",
        "reddit.com",
        "youtube.com",
        "facebook.com",
        "twitter.com"
    ]
    
    with open("sample_domains.txt", "w") as f:
        for domain in sample_domains:
            f.write(f"{domain}\n")
    
    print("📁 Created sample_domains.txt")
    
    # Process the file
    checker = DomainChecker(max_concurrent=3, rate_limit=1.5)
    results = await checker.lookup_domains_from_file("sample_domains.txt")
    
    print(f"📊 File Processing Results:")
    print(f"   Total: {results.total_domains}")
    print(f"   Successful: {results.successful_lookups}")
    print(f"   Failed: {results.failed_lookups}")
    print(f"   Total Time: {results.total_time:.2f}s")
    
    # Save results to JSON
    results_data = {
        "summary": {
            "total_domains": results.total_domains,
            "successful_lookups": results.successful_lookups,
            "failed_lookups": results.failed_lookups,
            "total_time": results.total_time,
            "average_time_per_domain": results.average_time_per_domain
        },
        "results": [
            {
                "domain": r.domain,
                "success": r.success,
                "method": r.method,
                "lookup_time": r.lookup_time,
                "error": r.error,
                "data": {
                    "registrar": r.data.registrar if r.data else None,
                    "creation_date": r.data.creation_date.isoformat() if r.data and r.data.creation_date else None,
                    "expiration_date": r.data.expiration_date.isoformat() if r.data and r.data.expiration_date else None,
                    "status": r.data.status if r.data else [],
                    "name_servers": r.data.name_servers if r.data else [],
                    "source": r.data.source if r.data else None
                } if r.data else None
            }
            for r in results.results
        ]
    }
    
    with open("results.json", "w") as f:
        json.dump(results_data, f, indent=2, default=str)
    
    print("💾 Saved results to results.json")


async def error_handling_example():
    """Example: Error handling"""
    print("\n=== Error Handling ===")
    
    checker = DomainChecker()
    
    # Test with invalid domain
    try:
        result = await checker.lookup_domain("invalid-domain-name-that-does-not-exist")
        if not result.success:
            print(f"❌ Expected failure for invalid domain: {result.error}")
    except Exception as e:
        print(f"❌ Exception for invalid domain: {e}")
    
    # Test with valid domain
    try:
        result = await checker.lookup_domain("example.com")
        if result.success:
            print(f"✅ Successfully looked up valid domain: {result.data.domain}")
        else:
            print(f"❌ Unexpected failure for valid domain: {result.error}")
    except Exception as e:
        print(f"❌ Unexpected exception for valid domain: {e}")


async def main():
    """Run all examples"""
    print("🚀 Domain Checker Examples\n")
    
    try:
        await single_domain_lookup()
        await bulk_domain_lookup()
        await method_comparison()
        await file_processing()
        await error_handling_example()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
    
    finally:
        # Cleanup
        import os
        if os.path.exists("sample_domains.txt"):
            os.remove("sample_domains.txt")
        if os.path.exists("results.json"):
            os.remove("results.json")


if __name__ == "__main__":
    asyncio.run(main())
