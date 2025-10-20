# Domain Checker

An asynchronous domain checker with WHOIS, RDAP, and DIG support, featuring a beautiful CLI interface and MCP server connectivity.

## Features

- **Asynchronous Processing**: Fast, non-blocking domain lookups
- **Triple Protocol Support**: WHOIS, RDAP, and DIG lookups
- **DNS Record Types**: Support for A, AAAA, MX, NS, SOA, TXT, and ANY records
- **DNS Propagation Checker**: Check DNS resolution across 20 regional ISP resolvers
- **Reverse DNS**: IP address to hostname lookups
- **Bulk Processing**: Check multiple domains with rate limiting
- **Multiple Output Formats**: Rich (default), Plain, JSON, and CSV formats
- **Copy/Paste Friendly**: Plain text output without formatting or colors
- **Beautiful CLI**: Rich, colorful terminal interface with tables and panels
- **User-Friendly GUI**: Easy-to-use graphical interface for non-technical users
- **MCP Server**: Connect via Model Context Protocol
- **Configurable**: Extensive configuration options
- **Error Handling**: Robust error handling and validation

## Installation

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/TheZacillac/domain-checker.git
cd domain-checker

# Install with pipx (recommended)
pipx install -e .

# Alternative: Install with pip
pip install -e .
```

### Requirements

- **Python 3.8+** (required)

### Installation Methods

#### 1. pipx Installation (Recommended)
```bash
# Install with pipx for isolated environment
pipx install -e .

# Or install directly from GitHub
pipx install git+https://github.com/TheZacillac/domain-checker.git
```

#### 2. pip Installation (Alternative)
```bash
# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

#### 3. Development Installation
```bash
# Clone and install in development mode
git clone https://github.com/TheZacillac/domain-checker.git
cd domain-checker
pipx install -e .

# Install development dependencies (optional)
pip install pytest black flake8 mypy
```

### Post-Installation Setup

After installation, you may need to update your PATH:

```bash
# Add pipx to your PATH (if not already there)
pipx ensurepath

# Restart your terminal or source your shell config
source ~/.bashrc  # or ~/.zshrc
```

### Verification

After installation, verify everything works:

```bash
# Test basic functionality
domch lookup example.com

# Test bulk lookup
domch bulk example.com google.com

# Test interactive mode
domch interactive
```

## Quick Start

### GUI Usage (Recommended for Non-Technical Users)

Launch the user-friendly graphical interface:

```bash
domch gui
```

**Note**: If you get an error about missing `textual`, install it with:
```bash
# If you installed with pipx:
pipx inject domain-checker textual

# If you installed with pip:
pip install textual
```

The GUI provides:
- **🔍 Domain Lookup**: Simple form to check single domains
- **📋 Bulk Check**: Check multiple domains at once
- **⚙️ Settings**: Configure preferences
- **❓ Help**: Built-in documentation
- **ℹ️ About**: Version and credit information

### CLI Usage (For Technical Users)

```bash
# Lookup a single domain
domch lookup example.com

# Lookup with specific method
domch lookup example.com --method rdap

# DIG lookup with specific record type
domch dig example.com --record A
domch dig example.com --record MX
domch dig example.com --record NS

# Reverse DNS lookup
domch reverse 8.8.8.8

# Check DNS propagation across regional ISPs
domch prop example.com --record A

# Bulk lookup with DIG
domch bulk example.com google.com --method dig --dig-record A

# Lookup from file
domch file domains.txt

# Compare WHOIS vs RDAP
domch compare example.com

# Interactive mode
domch interactive

# Output Formats - Get copy/paste friendly output
domch lookup example.com --format plain          # Clean text output
domch lookup example.com --format json           # JSON output
domch bulk example.com google.com --format csv   # CSV output for Excel
domch prop example.com --format json             # JSON for propagation check
```

### Python API

```python
import asyncio
from domain_checker import DomainChecker

async def main():
    checker = DomainChecker()
    
    # Single domain lookup
    result = await checker.lookup_domain("example.com")
    print(f"Domain: {result.domain}")
    print(f"Registrar: {result.data.registrar}")
    print(f"Expires: {result.data.expiration_date}")
    
    # Bulk lookup
    domains = ["example.com", "google.com", "github.com"]
    results = await checker.lookup_domains_bulk(domains)
    print(f"Successfully looked up {results.successful_lookups} domains")

asyncio.run(main())
```

### MCP Server

```bash
# Start MCP server
python -m domain_checker.mcp_server
```

## Configuration

Create a configuration file at `~/.config/domain-checker/config.json`:

```json
{
  "timeout": 30,
  "max_concurrent": 10,
  "rate_limit": 1.0,
  "default_method": "auto",
  "prefer_rdap": true,
  "show_raw_data": false,
  "enable_cache": false,
  "log_level": "INFO"
}
```

Or use environment variables:

```bash
export DOMAIN_CHECKER_TIMEOUT=30
export DOMAIN_CHECKER_MAX_CONCURRENT=10
export DOMAIN_CHECKER_RATE_LIMIT=1.0
export DOMAIN_CHECKER_DEFAULT_METHOD=auto
export DOMAIN_CHECKER_PREFER_RDAP=true
```

## CLI Commands

### `lookup`
Lookup a single domain with detailed information display.

```bash
domch lookup example.com [--method whois|rdap|dig|auto] [--timeout 30] [--raw] [--dig-record A|AAAA|MX|NS|SOA|TXT|ANY] [--format rich|plain|json]
```

**Output Formats:**
- `rich` (default) - Beautiful, colorful terminal output with tables and panels
- `plain` - Clean, copy/paste friendly text output without formatting
- `json` - Structured JSON output for programmatic use

### `bulk`
Lookup multiple domains with progress tracking.

```bash
domch bulk domain1.com domain2.com [--method auto] [--concurrent 10] [--rate-limit 1.0] [--dig-record A|AAAA|MX|NS|SOA|TXT|ANY] [--format rich|plain|json|csv]
```

**Output Formats:**
- `rich` (default) - Beautiful, colorful terminal output with tables
- `plain` - Clean, copy/paste friendly text output
- `json` - Structured JSON output for programmatic use
- `csv` - Comma-separated values for Excel/spreadsheet import

### `file`
Lookup domains from a text file (one domain per line).

```bash
domch file domains.txt [--method auto] [--concurrent 10] [--rate-limit 1.0] [--dig-record A|AAAA|MX|NS|SOA|TXT|ANY] [--format rich|plain|json|csv]
```

**Output Formats:**
- `rich` (default) - Beautiful, colorful terminal output with tables
- `plain` - Clean, copy/paste friendly text output
- `json` - Structured JSON output for programmatic use
- `csv` - Comma-separated values for Excel/spreadsheet import

### `dig`
Perform DIG lookup for a domain with specific DNS record type.

```bash
domch dig example.com [--record A|AAAA|MX|NS|SOA|TXT|ANY] [--timeout 30] [--format rich|plain|json]
```

**Output Formats:**
- `rich` (default) - Beautiful, colorful terminal output
- `plain` - Clean, copy/paste friendly text output
- `json` - Structured JSON output

### `reverse`
Perform reverse DNS lookup for an IP address.

```bash
domch reverse 8.8.8.8 [--timeout 30] [--format rich|plain|json]
```

**Output Formats:**
- `rich` (default) - Beautiful, colorful terminal output
- `plain` - Clean, copy/paste friendly text output
- `json` - Structured JSON output

### `compare`
Compare WHOIS and RDAP results for a domain.

```bash
domch compare example.com [--timeout 30]
```

### `interactive`
Start interactive mode for repeated lookups.

```bash
domch interactive
```

### `gui`
Launch the user-friendly graphical interface.

```bash
domch gui
```

**Features:**
- Easy-to-use form-based interface
- Tabbed navigation (Domain Lookup, Bulk Check, Settings, Help, About)
- Real-time results display
- Built-in help and documentation
- No command-line knowledge required

### `about`
Show version information and credits.

```bash
domch about
```

**Example Output:**
```
┌─ About Domain Checker ─┐
│ Domain Checker v1.1.0  │
│                        │
│ Created by: Zac Roach  │
│                        │
│ Description: Asynchronous domain checker with WHOIS, RDAP, and DIG support │
│                        │
│ Features:              │
│ • Fast asynchronous domain lookups │
│ • WHOIS, RDAP, and DIG protocol support │
│ • DNS propagation checking │
│ • Bulk domain processing │
│ • Beautiful CLI interface │
│ • MCP server integration │
│                        │
│ Repository: https://github.com/TheZacillac/domain-checker │
│ License: MIT           │
└────────────────────────┘
```

## GUI Interface

Domain Checker includes a user-friendly graphical interface that makes domain checking accessible to non-technical users.

### Launching the GUI

```bash
domch gui
```

**Installation Note**: If you get an error about missing `textual`, install it with:
```bash
# If you installed with pipx:
pipx inject domain-checker textual

# If you installed with pip:
pip install textual
```

### GUI Features

#### 🔍 Domain Lookup Tab
- Simple form to enter domain names
- Dropdown to select lookup method (Auto, WHOIS, RDAP, DIG)
- Real-time results display with emojis and formatting
- Easy-to-read information layout

#### 📋 Bulk Check Tab
- Text area to enter multiple domains (one per line)
- Configurable concurrent lookups
- Results table with status indicators
- Summary statistics

#### ⚙️ Settings Tab
- **General**: Default method, timeout, concurrent lookups
- **Display**: Show emojis, raw data, auto-scroll, colorize
- **Advanced**: Rate limiting, user agent

#### ❓ Help Tab
- **Getting Started**: Basic usage instructions
- **Methods**: Explanation of WHOIS, RDAP, DIG
- **Troubleshooting**: Common issues and solutions

#### ℹ️ About Tab
- Version information
- Feature list
- Credits and license
- Repository links

### GUI Benefits

- **No Command Line Knowledge Required**: Point-and-click interface
- **Visual Feedback**: Emojis and colors make results easy to understand
- **Built-in Help**: Documentation is integrated into the interface
- **Error Handling**: User-friendly error messages
- **Settings Management**: Easy configuration without editing files

### Keyboard Shortcuts

- `Tab` / `Shift+Tab`: Navigate between fields
- `Enter`: Submit forms or activate buttons
- `Ctrl+C` / `Q`: Quit the application
- `F1` / `Ctrl+H`: Show help
- `Ctrl+Tab`: Switch between tabs

## Output Formats

Domain Checker supports multiple output formats to suit different needs. Use the `--format` (or `-f`) flag to specify your preferred format.

### Rich Format (Default)
Beautiful, colorful terminal output with tables, panels, and emojis. Best for interactive use.

```bash
domch lookup example.com --format rich
# or simply
domch lookup example.com
```

### Plain Format
Clean, copy/paste friendly text output without any formatting, colors, or emojis. Perfect for:
- Copying data to other applications
- Parsing output in scripts
- Viewing in text editors
- Terminal environments without color support

```bash
domch lookup example.com --format plain
```

**Example Output:**
```
============================================================
DOMAIN INFORMATION
============================================================
Domain: example.com
Method: RDAP
Lookup Time: 0.45s
Registrar: IANA
Status: active

NAME SERVERS:
  a.iana-servers.net
  b.iana-servers.net

IMPORTANT DATES:
  Creation: 1995-08-14 04:00:00
  Expiration: 2024-08-13 04:00:00
  Last Updated: 2023-08-14 07:01:38
============================================================
```

### JSON Format
Structured JSON output for programmatic use and integration with other tools.

```bash
domch lookup example.com --format json
```

**Example Output:**
```json
{
  "domain": "example.com",
  "success": true,
  "method": "rdap",
  "lookup_time": 0.45,
  "registration_status": "registered",
  "error": null,
  "data": {
    "domain": "example.com",
    "registrar": "IANA",
    "creation_date": "1995-08-14T04:00:00",
    "expiration_date": "2024-08-13T04:00:00",
    "updated_date": "2023-08-14T07:01:38",
    "status": ["active"],
    "name_servers": ["a.iana-servers.net", "b.iana-servers.net"],
    "source": "rdap"
  }
}
```

### CSV Format (Bulk Operations Only)
Comma-separated values format, perfect for importing into Excel or other spreadsheet applications.

```bash
domch bulk example.com google.com github.com --format csv
# or save to file
domch file domains.txt --format csv > results.csv
```

**Example Output:**
```
Domain,Registration Status,Method,Lookup Time (s),Registrar,Creation Date,Expiration Date,Status
example.com,registered,RDAP,0.45,IANA,1995-08-14,2024-08-13,active
google.com,registered,RDAP,0.52,MarkMonitor Inc.,1997-09-15,2028-09-14,clientTransferProhibited
github.com,registered,RDAP,0.48,MarkMonitor Inc.,2007-10-09,2024-10-09,clientTransferProhibited
```

### Format Support by Command

| Command | Rich | Plain | JSON | CSV |
|---------|------|-------|------|-----|
| `lookup` | ✅ | ✅ | ✅ | ❌ |
| `bulk` | ✅ | ✅ | ✅ | ✅ |
| `file` | ✅ | ✅ | ✅ | ✅ |
| `dig` | ✅ | ✅ | ✅ | ❌ |
| `reverse` | ✅ | ✅ | ✅ | ❌ |
| `prop` | ✅ | ✅ | ✅ | ❌ |
| `compare` | ✅ | ❌ | ❌ | ❌ |
| `interactive` | ✅ | ❌ | ❌ | ❌ |

### Use Cases

**For Copy/Paste:**
```bash
# Get clean name servers list
domch lookup example.com --format plain | grep -A 10 "NAME SERVERS"

# Get just the IP addresses from propagation check
domch prop example.com --format plain | grep -A 100 "RESOLVED IP"
```

**For Scripts:**
```bash
# Parse JSON with jq
domch lookup example.com --format json | jq '.data.registrar'

# Check if domain is registered
domch lookup example.com --format json | jq -r '.registration_status'
```

**For Spreadsheets:**
```bash
# Export bulk results to Excel
domch file domains.txt --format csv > domains.csv

# Bulk check with CSV output
domch bulk domain1.com domain2.com domain3.com --format csv > results.csv
```

## API Reference

### DomainChecker

Main class for domain lookups.

```python
checker = DomainChecker(
    timeout=30,           # Timeout in seconds
    max_concurrent=10,    # Max concurrent lookups
    rate_limit=1.0        # Rate limit (requests/second)
)
```

#### Methods

- `lookup_domain(domain, method="auto")` - Lookup single domain
- `lookup_domains_bulk(domains, method="auto")` - Bulk lookup
- `lookup_domains_from_file(file_path, method="auto")` - Lookup from file
- `compare_methods(domain)` - Compare WHOIS vs RDAP

### Models

#### DomainInfo
Contains domain information from WHOIS or RDAP.

```python
class DomainInfo:
    domain: str
    registrar: Optional[str]
    creation_date: Optional[datetime]
    expiration_date: Optional[datetime]
    updated_date: Optional[datetime]
    status: List[str]
    name_servers: List[str]
    registrant: Optional[Dict]
    admin_contact: Optional[Dict]
    tech_contact: Optional[Dict]
    source: str  # "whois" or "rdap"
```

#### LookupResult
Result of a domain lookup operation.

```python
class LookupResult:
    domain: str
    success: bool
    data: Optional[DomainInfo]
    error: Optional[str]
    lookup_time: float
    method: str
```

## MCP Server

The MCP server provides programmatic access to domain checking functionality.

### Available Tools

- `lookup_domain` - Lookup single domain
- `lookup_domains_bulk` - Bulk domain lookup
- `compare_methods` - Compare WHOIS vs RDAP
- `lookup_domains_from_file` - Lookup from file

### Example MCP Client

```python
import asyncio
from mcp.client import Client

async def main():
    client = Client("domain-checker")
    await client.connect()
    
    # Lookup a domain
    result = await client.call_tool("lookup_domain", {
        "domain": "example.com",
        "method": "auto"
    })
    
    print(result)

asyncio.run(main())
```

## Examples

### Basic Usage

```python
import asyncio
from domain_checker import DomainChecker

async def single_domain_lookup():
    """Example: Lookup a single domain"""
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

asyncio.run(single_domain_lookup())
```

### Bulk Processing

```python
import asyncio
from domain_checker import DomainChecker

async def bulk_domain_lookup():
    """Example: Bulk domain lookup"""
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

asyncio.run(bulk_domain_lookup())
```

### Method Comparison

```python
import asyncio
from domain_checker import DomainChecker

async def method_comparison():
    """Example: Compare WHOIS vs RDAP"""
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

asyncio.run(method_comparison())
```

### File Processing

```python
import asyncio
import json
from domain_checker import DomainChecker

async def file_processing():
    """Example: Process domains from file"""
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

asyncio.run(file_processing())
```

### DIG Lookups

```python
import asyncio
from domain_checker import DomainChecker

async def dig_examples():
    """Examples of DIG functionality"""
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

asyncio.run(dig_examples())
```

### Advanced Usage

```python
import asyncio
import json
import time
from typing import List
from domain_checker import DomainChecker
from domain_checker.exceptions import ValidationError, TimeoutError
from domain_checker.utils import validate_domains, create_summary_stats

async def custom_configuration():
    """Example: Custom configuration"""
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

async def performance_benchmark():
    """Example: Performance benchmarking"""
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

# Run examples
asyncio.run(custom_configuration())
asyncio.run(performance_benchmark())
```

### MCP Server Usage

```python
import asyncio
import json
from mcp.client import Client

async def mcp_client_example():
    """Example: Using domain checker via MCP"""
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
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.disconnect()
        print("👋 Disconnected from MCP server")

asyncio.run(mcp_client_example())
```

## Error Handling

The library provides comprehensive error handling:

```python
from domain_checker.exceptions import (
    DomainLookupError,
    WhoisError,
    RdapError,
    ValidationError,
    TimeoutError
)

try:
    result = await checker.lookup_domain("invalid-domain")
except ValidationError as e:
    print(f"Invalid domain: {e}")
except TimeoutError as e:
    print(f"Lookup timed out: {e}")
except DomainLookupError as e:
    print(f"Lookup failed: {e}")
```

## Performance Tips

1. **Use appropriate concurrency**: Set `max_concurrent` based on your system and network capacity
2. **Rate limiting**: Use `rate_limit` to avoid overwhelming servers
3. **Method selection**: RDAP is generally faster than WHOIS
4. **Batch processing**: Use bulk operations for multiple domains
5. **pipx installation**: Use pipx for better isolation and performance

## Troubleshooting

### Common Issues

#### 1. Python Version Error
```
❌ Python 3.8+ is required. Found: 3.7
```
**Solution**: Upgrade Python to 3.8 or higher

#### 2. Permission Denied
```
❌ Permission denied: /usr/local/bin/domch
```
**Solution**: Use pipx for isolated installation: `pipx install -e .`

#### 3. Externally Managed Environment
```
❌ externally-managed-environment
```
**Solution**: Use pipx for installation: `pipx install -e .`

#### 4. Import Error
```
❌ ModuleNotFoundError: No module named 'domain_checker'
```
**Solution**: Reinstall the package with `pipx reinstall domain-checker`

#### 5. Command Not Found
```
❌ domch: command not found
```
**Solution**: 
1. First, ensure pipx is in your PATH: `pipx ensurepath`
2. Restart your terminal or run: `source ~/.bashrc` (or `~/.zshrc`)
3. If still not found, reinstall: `pipx reinstall domain-checker`

### Performance Issues

#### Slow Lookups
- **Cause**: Network latency or rate limiting
- **Solution**: Adjust `--rate-limit` and `--concurrent` parameters

#### High Memory Usage
- **Cause**: Large bulk operations
- **Solution**: Reduce `--concurrent` parameter or process in smaller batches

### Network Issues

#### WHOIS Timeouts
- **Cause**: WHOIS servers are slow or unresponsive
- **Solution**: Use `--method rdap` or increase `--timeout`

#### RDAP Failures
- **Cause**: RDAP servers are down or domain not supported
- **Solution**: Use `--method whois` or `--method auto`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the examples

## Changelog

### v1.0.0
- Initial release
- WHOIS and RDAP support
- CLI interface
- MCP server
- Bulk processing
- Configuration system
- Error handling
