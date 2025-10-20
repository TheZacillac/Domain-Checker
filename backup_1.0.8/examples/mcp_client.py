#!/usr/bin/env python3
"""
MCP client example for domain checker
"""

import asyncio
import json
from mcp.client import Client


async def mcp_client_example():
    """Example: Using domain checker via MCP"""
    print("=== MCP Client Example ===")
    
    # Connect to MCP server
    client = Client("domain-checker")
    
    try:
        await client.connect()
        print("✅ Connected to MCP server")
        
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        
        # Lookup a single domain
        print("\n🔍 Looking up example.com...")
        result = await client.call_tool("lookup_domain", {
            "domain": "example.com",
            "method": "auto",
            "timeout": 30
        })
        
        if result and result.content:
            data = json.loads(result.content[0].text)
            print(f"✅ Domain: {data['domain']}")
            print(f"📋 Success: {data['success']}")
            print(f"⏱️  Time: {data['lookup_time']:.2f}s")
            print(f"🔧 Method: {data['method']}")
            
            if data['data']:
                print(f"🏢 Registrar: {data['data']['registrar']}")
                print(f"📅 Creation: {data['data']['creation_date']}")
                print(f"⏰ Expiration: {data['data']['expiration_date']}")
        
        # Bulk lookup
        print("\n🔍 Bulk lookup...")
        bulk_result = await client.call_tool("lookup_domains_bulk", {
            "domains": ["google.com", "github.com", "stackoverflow.com"],
            "method": "auto",
            "timeout": 30,
            "max_concurrent": 5,
            "rate_limit": 1.0
        })
        
        if bulk_result and bulk_result.content:
            data = json.loads(bulk_result.content[0].text)
            print(f"📊 Bulk Results:")
            print(f"   Total: {data['total_domains']}")
            print(f"   Successful: {data['successful_lookups']}")
            print(f"   Failed: {data['failed_lookups']}")
            print(f"   Total Time: {data['total_time']:.2f}s")
            
            for result in data['results']:
                if result['success']:
                    print(f"   ✅ {result['domain']}: {result['data']['registrar'] if result['data'] else 'N/A'}")
                else:
                    print(f"   ❌ {result['domain']}: {result['error']}")
        
        # Compare methods
        print("\n🔍 Comparing methods...")
        compare_result = await client.call_tool("compare_methods", {
            "domain": "example.com",
            "timeout": 30
        })
        
        if compare_result and compare_result.content:
            data = json.loads(compare_result.content[0].text)
            print(f"📊 Method Comparison for {data['domain']}:")
            print(f"   WHOIS Success: {'✅' if data['whois']['success'] else '❌'} ({data['whois']['lookup_time']:.2f}s)")
            print(f"   RDAP Success: {'✅' if data['rdap']['success'] else '❌'} ({data['rdap']['lookup_time']:.2f}s)")
        
        # Lookup from file
        print("\n🔍 Lookup from file...")
        
        # Create a sample file
        with open("mcp_domains.txt", "w") as f:
            f.write("google.com\ngithub.com\nstackoverflow.com\n")
        
        file_result = await client.call_tool("lookup_domains_from_file", {
            "file_path": "mcp_domains.txt",
            "method": "auto",
            "timeout": 30,
            "max_concurrent": 3,
            "rate_limit": 1.0
        })
        
        if file_result and file_result.content:
            data = json.loads(file_result.content[0].text)
            print(f"📁 File Results:")
            print(f"   Total: {data['total_domains']}")
            print(f"   Successful: {data['successful_lookups']}")
            print(f"   Failed: {data['failed_lookups']}")
        
        # Cleanup
        import os
        if os.path.exists("mcp_domains.txt"):
            os.remove("mcp_domains.txt")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.disconnect()
        print("👋 Disconnected from MCP server")


async def main():
    """Main entry point"""
    print("🚀 MCP Client Example\n")
    
    try:
        await mcp_client_example()
        print("\n✅ MCP client example completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running MCP client example: {e}")


if __name__ == "__main__":
    asyncio.run(main())
