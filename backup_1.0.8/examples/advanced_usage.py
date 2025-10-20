#!/usr/bin/env python3
"""
Advanced usage examples for domain checker
"""

import asyncio
import json
import time
from typing import List
from domain_checker import DomainChecker
from domain_checker.exceptions import ValidationError, TimeoutError
from domain_checker.utils import validate_domains, create_summary_stats


async def custom_configuration():
    """Example: Custom configuration"""
    print("=== Custom Configuration ===")
    
    # Create checker with custom settings
    checker = DomainChecker(
        timeout=60,           # Longer timeout
        max_concurrent=20,    # More concurrent requests
        rate_limit=0.5        # Slower rate limit
    )
    
    print(f"🔧 Configuration:")
    print(f"   Timeout: 60s")
    print(f"   Max Concurrent: 20")
    print(f"   Rate Limit: 0.5 req/s")
    
    # Test with a domain
    result = await checker.lookup_domain("example.com")
    print(f"✅ Lookup completed in {result.lookup_time:.2f}s")


async def domain_validation():
    """Example: Domain validation"""
    print("\n=== Domain Validation ===")
    
    test_domains = [
        "example.com",           # Valid
        "sub.example.com",       # Valid subdomain
        "example.co.uk",         # Valid with country code
        "invalid-domain",        # Invalid (no TLD)
        "example..com",          # Invalid (double dot)
        "example.com.",          # Valid (trailing dot)
        "EXAMPLE.COM",           # Valid (will be lowercased)
        "http://example.com",    # Valid (protocol will be stripped)
        "www.example.com",       # Valid (www will be stripped)
    ]
    
    print("🔍 Testing domain validation:")
    
    for domain in test_domains:
        try:
            validated = validate_domains([domain])[0]
            print(f"   ✅ {domain} -> {validated}")
        except ValidationError as e:
            print(f"   ❌ {domain} -> {e}")


async def performance_benchmark():
    """Example: Performance benchmarking"""
    print("\n=== Performance Benchmark ===")
    
    domains = [
        "example.com", "google.com", "github.com", "stackoverflow.com",
        "reddit.com", "youtube.com", "facebook.com", "twitter.com",
        "linkedin.com", "instagram.com", "amazon.com", "microsoft.com"
    ]
    
    # Test different configurations
    configurations = [
        {"max_concurrent": 1, "rate_limit": 0.5, "name": "Conservative"},
        {"max_concurrent": 5, "rate_limit": 1.0, "name": "Balanced"},
        {"max_concurrent": 10, "rate_limit": 2.0, "name": "Aggressive"},
    ]
    
    results = {}
    
    for config in configurations:
        print(f"\n🔧 Testing {config['name']} configuration...")
        
        checker = DomainChecker(
            max_concurrent=config['max_concurrent'],
            rate_limit=config['rate_limit']
        )
        
        start_time = time.time()
        bulk_results = await checker.lookup_domains_bulk(domains)
        end_time = time.time()
        
        results[config['name']] = {
            'total_time': end_time - start_time,
            'successful': bulk_results.successful_lookups,
            'failed': bulk_results.failed_lookups,
            'average_time': bulk_results.average_time_per_domain
        }
        
        print(f"   ⏱️  Total Time: {results[config['name']]['total_time']:.2f}s")
        print(f"   ✅ Successful: {results[config['name']]['successful']}")
        print(f"   ❌ Failed: {results[config['name']]['failed']}")
        print(f"   📊 Average per Domain: {results[config['name']]['average_time']:.2f}s")
    
    # Find best configuration
    best_config = min(results.items(), key=lambda x: x[1]['total_time'])
    print(f"\n🏆 Best Configuration: {best_config[0]}")
    print(f"   Time: {best_config[1]['total_time']:.2f}s")


async def error_handling_advanced():
    """Example: Advanced error handling"""
    print("\n=== Advanced Error Handling ===")
    
    checker = DomainChecker(timeout=5)  # Short timeout for testing
    
    test_cases = [
        {"domain": "example.com", "expected": "success"},
        {"domain": "nonexistent-domain-12345.com", "expected": "failure"},
        {"domain": "invalid-domain", "expected": "validation_error"},
    ]
    
    for test_case in test_cases:
        domain = test_case["domain"]
        expected = test_case["expected"]
        
        print(f"\n🔍 Testing: {domain} (expected: {expected})")
        
        try:
            result = await checker.lookup_domain(domain)
            
            if expected == "success":
                if result.success:
                    print(f"   ✅ Expected success, got success")
                else:
                    print(f"   ❌ Expected success, got failure: {result.error}")
            elif expected == "failure":
                if not result.success:
                    print(f"   ✅ Expected failure, got failure: {result.error}")
                else:
                    print(f"   ❌ Expected failure, got success")
            
        except ValidationError as e:
            if expected == "validation_error":
                print(f"   ✅ Expected validation error, got: {e}")
            else:
                print(f"   ❌ Unexpected validation error: {e}")
        except TimeoutError as e:
            print(f"   ⏰ Timeout error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")


async def data_analysis():
    """Example: Data analysis and statistics"""
    print("\n=== Data Analysis ===")
    
    checker = DomainChecker()
    
    # Lookup multiple domains
    domains = [
        "example.com", "google.com", "github.com", "stackoverflow.com",
        "reddit.com", "youtube.com", "facebook.com", "twitter.com"
    ]
    
    results = await checker.lookup_domains_bulk(domains)
    
    # Convert to format expected by create_summary_stats
    results_data = [
        {
            "success": r.success,
            "method": r.method,
            "lookup_time": r.lookup_time,
            "domain": r.domain
        }
        for r in results.results
    ]
    
    # Generate statistics
    stats = create_summary_stats(results_data)
    
    print(f"📊 Analysis Results:")
    print(f"   Total Domains: {stats['total']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    print(f"   Average Time: {stats['average_time']:.2f}s")
    print(f"   Fastest Lookup: {stats['fastest']:.2f}s")
    print(f"   Slowest Lookup: {stats['slowest']:.2f}s")
    print(f"   Total Time: {stats['total_time']:.2f}s")
    
    print(f"\n📋 Method Distribution:")
    for method, count in stats['methods'].items():
        print(f"   {method}: {count} lookups")
    
    # Analyze by registrar
    registrars = {}
    for result in results.results:
        if result.success and result.data and result.data.registrar:
            registrar = result.data.registrar
            registrars[registrar] = registrars.get(registrar, 0) + 1
    
    if registrars:
        print(f"\n🏢 Registrar Distribution:")
        for registrar, count in sorted(registrars.items(), key=lambda x: x[1], reverse=True):
            print(f"   {registrar}: {count} domains")


async def caching_example():
    """Example: Caching (if implemented)"""
    print("\n=== Caching Example ===")
    
    # Note: This is a placeholder for caching functionality
    # In a real implementation, you would enable caching in the configuration
    
    checker = DomainChecker()
    
    domain = "example.com"
    
    # First lookup (cache miss)
    print(f"🔍 First lookup of {domain}...")
    start_time = time.time()
    result1 = await checker.lookup_domain(domain)
    time1 = time.time() - start_time
    print(f"   Time: {time1:.2f}s")
    
    # Second lookup (would be cache hit if caching was enabled)
    print(f"🔍 Second lookup of {domain}...")
    start_time = time.time()
    result2 = await checker.lookup_domain(domain)
    time2 = time.time() - start_time
    print(f"   Time: {time2:.2f}s")
    
    print(f"📊 Time difference: {abs(time1 - time2):.2f}s")
    print(f"💡 Note: Caching is not implemented in this version")


async def export_results():
    """Example: Export results to different formats"""
    print("\n=== Export Results ===")
    
    checker = DomainChecker()
    
    domains = ["example.com", "google.com", "github.com"]
    results = await checker.lookup_domains_bulk(domains)
    
    # Export to JSON
    json_data = {
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
    
    with open("exported_results.json", "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    
    print("💾 Exported results to exported_results.json")
    
    # Export to CSV (simple format)
    import csv
    with open("exported_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Domain", "Success", "Method", "Lookup Time", "Registrar", "Creation Date", "Expiration Date"])
        
        for r in results.results:
            writer.writerow([
                r.domain,
                r.success,
                r.method,
                r.lookup_time,
                r.data.registrar if r.data else None,
                r.data.creation_date.isoformat() if r.data and r.data.creation_date else None,
                r.data.expiration_date.isoformat() if r.data and r.data.expiration_date else None
            ])
    
    print("💾 Exported results to exported_results.csv")
    
    # Cleanup
    import os
    if os.path.exists("exported_results.json"):
        os.remove("exported_results.json")
    if os.path.exists("exported_results.csv"):
        os.remove("exported_results.csv")


async def main():
    """Run all advanced examples"""
    print("🚀 Advanced Domain Checker Examples\n")
    
    try:
        await custom_configuration()
        await domain_validation()
        await performance_benchmark()
        await error_handling_advanced()
        await data_analysis()
        await caching_example()
        await export_results()
        
        print("\n✅ All advanced examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running advanced examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())
