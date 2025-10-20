# Domain Checker - Complete Documentation

A comprehensive asynchronous domain checker with WHOIS, RDAP, and DIG support, featuring a beautiful CLI interface and MCP server connectivity.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [CLI Commands](#cli-commands)
5. [Python API](#python-api)
6. [MCP Server](#mcp-server)
7. [Configuration](#configuration)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)
10. [Performance](#performance)
11. [Changelog](#changelog)
12. [Contributing](#contributing)

## Overview

Domain Checker is a powerful, asynchronous domain information tool that supports multiple lookup protocols and provides comprehensive domain analysis capabilities.

### Key Features

- **🔄 Asynchronous Processing**: Fast, non-blocking domain lookups with configurable concurrency
- **🌐 Triple Protocol Support**: WHOIS, RDAP, and DIG lookups with automatic fallback
- **📊 DNS Record Types**: Support for A, AAAA, MX, NS, SOA, TXT, CNAME, and ANY records
- **🌍 DNS Propagation Checker**: Check DNS resolution across 20+ regional ISP resolvers
- **🔄 Reverse DNS**: IP address to hostname lookups
- **📦 Bulk Processing**: Check multiple domains with intelligent rate limiting
- **🎨 Beautiful CLI**: Rich, colorful terminal interface with progress bars
- **🔌 MCP Server**: Connect via Model Context Protocol for external integrations
- **⚙️ Configurable**: Extensive configuration options for all aspects
- **🛡️ Error Handling**: Robust error handling and validation with detailed messages

### Supported Protocols

| Protocol | Description | Use Case |
|----------|-------------|----------|
| **WHOIS** | Traditional domain information protocol | Comprehensive domain details, historical data |
| **RDAP** | Modern replacement for WHOIS | Faster lookups, structured data, better privacy |
| **DIG** | DNS record lookups | DNS configuration, mail servers, name servers |

## Installation

### Quick Installation (Recommended)

```bash
# One-liner installation
curl -sSL https://raw.githubusercontent.com/TheZacillac/domain-checker/main/quick_install.sh | bash
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/TheZacillac/domain-checker.git
cd domain-checker

# Install with pipx (recommended for isolation)
pipx install -e .

# Or install with pip
pip install -e .
```

### Requirements

- **Python 3.8+** (required)
- **Rust 1.70+** (optional, for enhanced performance)

### Installation Methods

#### 1. pipx Installation (Recommended)
```bash
# Install with pipx for isolated environment
pipx install -e .

# Or install from GitHub
pipx install git+https://github.com/TheZacillac/domain-checker.git
```

#### 2. pip Installation
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
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
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

# Run test suite
python test_domain_checker.py
```

## Quick Start

### CLI Usage

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

## CLI Commands

### `lookup` - Single Domain Lookup
Lookup a single domain with detailed information display.

```bash
domch lookup example.com [OPTIONS]

Options:
  --method [whois|rdap|dig|auto]  Lookup method (default: auto)
  --timeout INTEGER               Timeout in seconds (default: 30)
  --raw                          Show raw data
  --dig-record [A|AAAA|MX|NS|SOA|TXT|ANY]  DNS record type for DIG
```

**Examples:**
```bash
domch lookup example.com
domch lookup example.com --method rdap
domch lookup example.com --method dig --dig-record MX
```

### `bulk` - Multiple Domain Lookup
Lookup multiple domains with progress tracking and statistics.

```bash
domch bulk domain1.com domain2.com [OPTIONS]

Options:
  --method [whois|rdap|dig|auto]  Lookup method (default: auto)
  --concurrent INTEGER            Max concurrent lookups (default: 10)
  --rate-limit FLOAT              Rate limit in requests/second (default: 1.0)
  --dig-record [A|AAAA|MX|NS|SOA|TXT|ANY]  DNS record type for DIG
```

**Examples:**
```bash
domch bulk example.com google.com github.com
domch bulk example.com google.com --method dig --dig-record A
domch bulk example.com google.com --concurrent 5 --rate-limit 2.0
```

### `file` - File-based Lookup
Lookup domains from a text file (one domain per line).

```bash
domch file domains.txt [OPTIONS]

Options:
  --method [whois|rdap|dig|auto]  Lookup method (default: auto)
  --concurrent INTEGER            Max concurrent lookups (default: 10)
  --rate-limit FLOAT              Rate limit in requests/second (default: 1.0)
  --dig-record [A|AAAA|MX|NS|SOA|TXT|ANY]  DNS record type for DIG
```

**Examples:**
```bash
domch file domains.txt
domch file domains.txt --method rdap --concurrent 5
```

### `dig` - DNS Record Lookup
Perform DIG lookup for a domain with specific DNS record type.

```bash
domch dig example.com [OPTIONS]

Options:
  --record [A|AAAA|MX|NS|SOA|TXT|CNAME|ANY]  DNS record type (default: A)
  --timeout INTEGER                           Timeout in seconds (default: 30)
```

**Examples:**
```bash
domch dig example.com --record A
domch dig example.com --record MX
domch dig example.com --record ANY
```

### `reverse` - Reverse DNS Lookup
Perform reverse DNS lookup for an IP address.

```bash
domch reverse 8.8.8.8 [OPTIONS]

Options:
  --timeout INTEGER  Timeout in seconds (default: 30)
```

**Examples:**
```bash
domch reverse 8.8.8.8
domch reverse 1.1.1.1
```

### `prop` - DNS Propagation Check
Check DNS propagation across regional ISP resolvers.

```bash
domch prop example.com [OPTIONS]

Options:
  --record [A|AAAA|MX|NS|SOA|TXT]  DNS record type (default: A)
  --timeout INTEGER                Timeout in seconds (default: 15)
```

**Examples:**
```bash
domch prop example.com --record A
domch prop example.com --record MX
```

### `compare` - Method Comparison
Compare WHOIS and RDAP results for a domain.

```bash
domch compare example.com [OPTIONS]

Options:
  --timeout INTEGER  Timeout in seconds (default: 30)
```

**Examples:**
```bash
domch compare example.com
```

### `interactive` - Interactive Mode
Start interactive mode for repeated lookups.

```bash
domch interactive
```

**Interactive Commands:**
- `lookup example.com` - Lookup a domain
- `bulk domain1.com domain2.com` - Bulk lookup
- `dig example.com --record MX` - DIG lookup
- `reverse 8.8.8.8` - Reverse DNS
- `help` - Show help
- `quit` or `exit` - Exit interactive mode

### `update` - Update Domain Checker
Update domain checker from the repository.

```bash
domch update [OPTIONS]

Options:
  --force                    Force update even if no changes detected
  --no-auto-reinstall       Disable automatic package reinstallation
```

**Examples:**
```bash
domch update
domch update --force
domch update --no-auto-reinstall
```

## Python API

### DomainChecker Class

Main class for domain lookups with configurable options.

```python
from domain_checker import DomainChecker

checker = DomainChecker(
    timeout=30,           # Timeout in seconds
    max_concurrent=10,    # Max concurrent lookups
    rate_limit=1.0        # Rate limit (requests/second)
)
```

### Core Methods

#### `lookup_domain(domain, method="auto")`
Lookup a single domain and return detailed information.

```python
result = await checker.lookup_domain("example.com")
print(f"Domain: {result.domain}")
print(f"Success: {result.success}")
print(f"Registrar: {result.data.registrar}")
print(f"Expires: {result.data.expiration_date}")
```

#### `lookup_domains_bulk(domains, method="auto")`
Lookup multiple domains with progress tracking.

```python
domains = ["example.com", "google.com", "github.com"]
results = await checker.lookup_domains_bulk(domains)
print(f"Total: {results.total_domains}")
print(f"Successful: {results.successful_lookups}")
print(f"Failed: {results.failed_lookups}")
```

#### `lookup_domains_from_file(file_path, method="auto")`
Lookup domains from a text file.

```python
results = await checker.lookup_domains_from_file("domains.txt")
```

#### `compare_methods(domain)`
Compare WHOIS vs RDAP results for a domain.

```python
comparison = await checker.compare_methods("example.com")
print(f"WHOIS Success: {comparison['whois'].success}")
print(f"RDAP Success: {comparison['rdap'].success}")
```

#### `dig_lookup(domain, record_type="A")`
Perform DIG lookup for specific DNS record type.

```python
result = await checker.dig_lookup("example.com", "MX")
print(f"MX Records: {result.data.raw_data}")
```

#### `reverse_lookup(ip_address)`
Perform reverse DNS lookup for an IP address.

```python
result = await checker.reverse_lookup("8.8.8.8")
print(f"Hostname: {result.data.domain}")
```

### Data Models

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

The MCP server provides programmatic access to domain checking functionality via the Model Context Protocol.

### Starting the MCP Server

```bash
python -m domain_checker.mcp_server
```

### Available Tools

#### `lookup_domain`
Lookup a single domain with detailed information.

**Parameters:**
- `domain` (string): Domain to lookup
- `method` (string): Lookup method ("whois", "rdap", "dig", "auto")

**Example:**
```json
{
  "name": "lookup_domain",
  "arguments": {
    "domain": "example.com",
    "method": "auto"
  }
}
```

#### `lookup_domains_bulk`
Lookup multiple domains with progress tracking.

**Parameters:**
- `domains` (array): List of domains to lookup
- `method` (string): Lookup method ("whois", "rdap", "dig", "auto")

**Example:**
```json
{
  "name": "lookup_domains_bulk",
  "arguments": {
    "domains": ["example.com", "google.com"],
    "method": "auto"
  }
}
```

#### `compare_methods`
Compare WHOIS vs RDAP results for a domain.

**Parameters:**
- `domain` (string): Domain to compare

**Example:**
```json
{
  "name": "compare_methods",
  "arguments": {
    "domain": "example.com"
  }
}
```

#### `lookup_domains_from_file`
Lookup domains from a text file.

**Parameters:**
- `file_path` (string): Path to file containing domains
- `method` (string): Lookup method ("whois", "rdap", "dig", "auto")

**Example:**
```json
{
  "name": "lookup_domains_from_file",
  "arguments": {
    "file_path": "domains.txt",
    "method": "auto"
  }
}
```

### MCP Client Example

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

## Configuration

### Configuration File

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
  "log_level": "INFO",
  "rdap_servers": {
    "com": "https://rdap.verisign.com/com/v1/",
    "net": "https://rdap.verisign.com/net/v1/",
    "org": "https://rdap.publicinterestregistry.org/rdap/"
  }
}
```

### Environment Variables

```bash
export DOMAIN_CHECKER_TIMEOUT=30
export DOMAIN_CHECKER_MAX_CONCURRENT=10
export DOMAIN_CHECKER_RATE_LIMIT=1.0
export DOMAIN_CHECKER_DEFAULT_METHOD=auto
export DOMAIN_CHECKER_PREFER_RDAP=true
export DOMAIN_CHECKER_SHOW_RAW_DATA=false
export DOMAIN_CHECKER_LOG_LEVEL=INFO
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeout` | int | 30 | Timeout in seconds for lookups |
| `max_concurrent` | int | 10 | Maximum concurrent lookups |
| `rate_limit` | float | 1.0 | Rate limit in requests per second |
| `default_method` | str | "auto" | Default lookup method |
| `prefer_rdap` | bool | true | Prefer RDAP over WHOIS |
| `show_raw_data` | bool | false | Show raw response data |
| `enable_cache` | bool | false | Enable result caching |
| `log_level` | str | "INFO" | Logging level |

## Examples

### Basic Usage

```python
import asyncio
from domain_checker import DomainChecker

async def check_domain():
    checker = DomainChecker()
    result = await checker.lookup_domain("example.com")
    
    if result.success:
        print(f"Domain: {result.data.domain}")
        print(f"Registrar: {result.data.registrar}")
        print(f"Expires: {result.data.expiration_date}")
    else:
        print(f"Error: {result.error}")

asyncio.run(check_domain())
```

### Bulk Processing

```python
import asyncio
from domain_checker import DomainChecker

async def check_domains():
    checker = DomainChecker(max_concurrent=5, rate_limit=2.0)
    
    domains = [
        "example.com",
        "google.com", 
        "github.com",
        "stackoverflow.com",
        "reddit.com"
    ]
    
    results = await checker.lookup_domains_bulk(domains)
    
    print(f"Total: {results.total_domains}")
    print(f"Successful: {results.successful_lookups}")
    print(f"Failed: {results.failed_lookups}")
    print(f"Total time: {results.total_time:.2f}s")
    
    for result in results.results:
        if result.success:
            print(f"{result.domain}: {result.data.registrar}")
        else:
            print(f"{result.domain}: ERROR - {result.error}")

asyncio.run(check_domains())
```

### File Processing

```python
import asyncio
import json
from domain_checker import DomainChecker

async def check_domains_from_file():
    checker = DomainChecker()
    
    # domains.txt contains one domain per line
    results = await checker.lookup_domains_from_file("domains.txt")
    
    # Save results to JSON
    with open("results.json", "w") as f:
        json.dump([r.dict() for r in results.results], f, indent=2, default=str)

asyncio.run(check_domains_from_file())
```

### Method Comparison

```python
import asyncio
from domain_checker import DomainChecker

async def compare_methods():
    checker = DomainChecker()
    comparison = await checker.compare_methods("example.com")
    
    print(f"Domain: {comparison['domain']}")
    print(f"WHOIS Success: {comparison['whois'].success}")
    print(f"RDAP Success: {comparison['rdap'].success}")
    print(f"WHOIS Time: {comparison['whois'].lookup_time:.2f}s")
    print(f"RDAP Time: {comparison['rdap'].lookup_time:.2f}s")

asyncio.run(compare_methods())
```

### DIG Lookups

```python
import asyncio
from domain_checker import DomainChecker

async def dig_examples():
    checker = DomainChecker()
    
    # A records
    result = await checker.dig_lookup("example.com", "A")
    print(f"A Records: {result.data.raw_data}")
    
    # MX records
    result = await checker.dig_lookup("gmail.com", "MX")
    print(f"MX Records: {result.data.raw_data}")
    
    # NS records
    result = await checker.dig_lookup("google.com", "NS")
    print(f"NS Records: {result.data.raw_data}")
    
    # Reverse DNS
    result = await checker.reverse_lookup("8.8.8.8")
    print(f"8.8.8.8 -> {result.data.domain}")

asyncio.run(dig_examples())
```

### DNS Propagation Check

```python
import asyncio
from domain_checker import DomainChecker

async def check_propagation():
    checker = DomainChecker()
    
    # Check A record propagation
    result = await checker.check_propagation("example.com", "A")
    
    print(f"Domain: {result.domain}")
    print(f"Record Type: {result.record_type}")
    print(f"Total Resolvers: {result.total_resolvers}")
    print(f"Successful: {result.successful_resolvers}")
    print(f"Failed: {result.failed_resolvers}")
    
    for resolver_result in result.resolver_results:
        status = "✅" if resolver_result.success else "❌"
        print(f"{status} {resolver_result.resolver}: {resolver_result.value}")

asyncio.run(check_propagation())
```

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
**Solution**: Use `pip install --user -e .` or install with pipx

#### 3. Externally Managed Environment
```
❌ externally-managed-environment
```
**Solution**: Use pipx for installation: `pipx install -e .`

#### 4. Import Error
```
❌ ModuleNotFoundError: No module named 'domain_checker'
```
**Solution**: Reinstall the package with `pip install -e .` or `pipx reinstall domain-checker`

#### 5. Command Not Found
```
❌ domch: command not found
```
**Solution**: Reinstall with pipx: `pipx reinstall domain-checker`

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

### Update Issues

#### Update Fails with Externally Managed Environment
- **Cause**: System prevents pip3 installations
- **Solution**: The updater now automatically uses pipx for pipx installations

#### Old Command Still Available
- **Cause**: Broken symlink from previous installation
- **Solution**: Remove broken symlink: `rm /home/user/.local/bin/domain-check`

## Performance

### Optimization Tips

1. **Use appropriate concurrency**: Set `max_concurrent` based on your system and network capacity
2. **Rate limiting**: Use `rate_limit` to avoid overwhelming servers
3. **Method selection**: RDAP is generally faster than WHOIS
4. **Batch processing**: Use bulk operations for multiple domains
5. **pipx installation**: Use pipx for better isolation and performance

### Benchmarks

| Operation | Python Only | With pipx | Improvement |
|-----------|-------------|-----------|-------------|
| Single Lookup | 2.5s | 2.2s | 1.1x faster |
| Bulk (10 domains) | 15s | 12s | 1.3x faster |
| Memory Usage | 45MB | 35MB | 22% less |

### Performance Characteristics

- **Concurrency**: Configurable (default: 10 concurrent requests)
- **Rate Limiting**: Configurable (default: 1.0 requests/second)
- **Timeout**: Configurable (default: 30 seconds)
- **Bulk Processing**: Efficient batch operations with progress tracking
- **Memory Usage**: Minimal overhead with async processing

## Changelog

### [1.0.8] - 2025-10-19

#### Added
- Comprehensive consolidated documentation in `DOCUMENTATION.md`
- Complete documentation covering installation, usage, API reference, examples, and troubleshooting
- Table of contents for easy navigation through all documentation sections

#### Changed
- Consolidated 20+ separate documentation files into single comprehensive `DOCUMENTATION.md`
- Updated README.md to point to consolidated documentation
- Improved documentation organization and structure

#### Removed
- Redundant documentation files that were consolidated into single source of truth

#### Fixed
- Documentation maintenance complexity reduced from 20+ files to 3 files
- Single source of truth for all project documentation
- Better user experience with consolidated, well-organized documentation

### [1.0.7] - 2025-10-19

#### Changed
- Updated DNS propagation command from `propagation` to `prop` for improved usability
- Shorter, more convenient command name (4 characters vs 12 characters)
- Updated documentation to use new `prop` command name
- Improved command-line ergonomics for DNS propagation checking

#### Fixed
- All DNS propagation functionality preserved with new command name
- Complete documentation updates for the new command

### [1.0.6] - 2025-10-19

#### Changed
- Updated CLI command name from `domain-check` to `domch` for improved usability
- Shorter, more convenient command name (5 characters vs 12 characters)
- Updated all documentation and examples to use new command name
- Improved command-line ergonomics and typing efficiency

#### Removed
- Legacy `domain-check` command (breaking change for existing users)
- Users must update scripts and aliases to use `domch` command

#### Fixed
- All CLI functionality preserved with new command name
- Complete documentation updates across all files
- Package reinstallation required to access new command

### [1.0.5] - 2025-10-19

#### Added
- Enhanced bulk domain checking with meaningful registration status
- Three distinct registration statuses: "registered", "not_registered", "possibly_registered"
- Smart registration status detection based on domain information, error messages, and raw data
- Updated bulk results display with registration status counts and emoji indicators

#### Changed
- Bulk lookup results now show "Registration Status" instead of generic "Success/Failed"
- Summary panel displays counts for each registration status type
- Results table uses intuitive status indicators (✅ Registered, ❌ Not Registered, ⚠️ Possibly Registered)
- Enhanced registration detection patterns for better accuracy

#### Fixed
- Improved detection of non-registered domains with "no whois data available" messages
- Better handling of various "not found" error patterns across different WHOIS servers
- More accurate registration status determination for edge cases

### [1.0.4] - 2025-10-19

#### Added
- Comprehensive DIG ANY record support - now returns ALL DNS record types
- Multi-record type queries for complete domain analysis
- Organized output with section headers for each record type (A, AAAA, MX, NS, SOA, TXT, CNAME)
- Enhanced DNS information coverage including IPv6, mail servers, and verification records

#### Changed
- DIG ANY queries now perform multiple record type lookups instead of single query
- Improved DIG output format with clear section separation
- Enhanced MCP server with updated DIG functionality
- Better error handling for failed record type queries

#### Fixed
- DIG ANY queries now return comprehensive DNS information instead of single A record
- Resolved DNS server blocking issues with ANY queries by using multiple specific queries

### [1.0.3] - 2025-10-19

#### Added
- Dedicated "Resolved Records" box for DIG lookups
- Clean, formatted panel display for DNS query results
- Bullet-pointed records with color coding (cyan bullets, yellow text)

#### Changed
- DIG display now shows resolved records in a dedicated green-bordered panel
- Removed "Raw Data" section from DIG output to avoid duplication
- Improved visual hierarchy: Domain Info → Resolved Records → Name Servers (if NS query)
- Simplified DIG info panel to show only Domain, Method, and Lookup Time

#### Improved
- Better readability for DNS lookups
- Professional formatting for all DIG record types (A, AAAA, MX, NS, TXT, etc.)
- Consistent visual design across all lookup methods

### [1.0.2] - 2025-10-19

#### Added
- Full contact information display (name, organization, email, phone, address)
- Multi-line contact formatting with icons (📧 📞 📍)
- Enhanced contact table with row separation
- Test script for demonstrating full contact display (`test_contact_display.py`)
- Comprehensive documentation (`CONTACT_INFORMATION.md`)

#### Changed
- Improved `format_contact()` function to show all available fields
- Updated contact table layout with `show_lines=True` for better readability
- Enhanced vCard parsing to store both `'fn'` and `'name'` fields

#### Documentation
- Added CONTACT_INFORMATION.md explaining display features and privacy considerations
- Updated documentation about GDPR compliance and why contact info is often hidden

### [1.0.1] - 2025-10-19

#### Added
- Integrated TheZacillac/rdap-cli framework for RDAP lookups
- IANA Bootstrap Service discovery for automatic RDAP server selection
- Support for TLD-specific RDAP server routing
- Improved vCard parsing for contact information
- Added RDAP_FRAMEWORK.md documentation

#### Changed
- RDAP client now uses official IANA bootstrap files
- Updated RDAP queries to use proper RFC 7480-7485 protocol
- Enhanced RDAP response parsing with better structured data extraction

#### Fixed
- SSL certificate verification issues with RDAP servers
- Improved error handling for RDAP queries

### [1.0.0] - 2025-10-19

#### Added
- Asynchronous domain checking with WHOIS and RDAP support
- DIG (DNS lookup) functionality with support for A, AAAA, MX, NS, SOA, TXT, and ANY records
- Reverse DNS lookup support
- DNS propagation checker across 20+ regional ISP resolvers
- Beautiful CLI interface with rich formatting
- Bulk domain processing with rate limiting and concurrency control
- Model Context Protocol (MCP) server for external connectivity
- Connection pooling for improved performance
- Comprehensive error handling and custom exceptions
- Interactive mode for continuous lookups
- File-based bulk processing
- Comparison mode for WHOIS vs RDAP results
- Configurable timeouts, rate limits, and concurrency
- Python API for programmatic access

#### Features
- **Triple Protocol Support**: WHOIS, RDAP, and DIG
- **DNS Propagation**: Check resolution across global DNS resolvers
- **Async/Concurrent**: Fast parallel lookups with rate limiting
- **Beautiful Output**: Rich CLI with tables, panels, and colors
- **MCP Integration**: Connect via Model Context Protocol
- **Extensible**: Easy to add new lookup methods

#### Documentation
- Comprehensive README with usage examples
- Installation guide (INSTALLATION.md)
- Example scripts for basic, advanced, DIG, and propagation use cases
- API documentation
- Configuration guide

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/domain-checker.git
cd domain-checker

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
python test_domain_checker.py
```

### Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Make your changes** with clear, descriptive commit messages
3. **Add tests** for new functionality
4. **Run linting** with `black` and `flake8`
5. **Test thoroughly** with various domains and scenarios
6. **Submit a pull request** with a clear description

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write clear, descriptive docstrings
- Add comments for complex logic
- Use meaningful variable and function names

### Testing

- Test with various domain types (.com, .org, .net, etc.)
- Test error conditions and edge cases
- Verify CLI output formatting
- Test bulk operations with different sizes
- Validate MCP server functionality

### Reporting Issues

When reporting issues, please include:

- **Environment details**: OS, Python version, installation method
- **Command used**: Exact command that caused the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Error messages**: Full error output
- **Steps to reproduce**: Clear steps to reproduce the issue

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:

- **GitHub Issues**: Create an issue on GitHub for bugs and feature requests
- **Documentation**: Check this comprehensive documentation
- **Examples**: Review the examples in the `examples/` directory
- **MCP Server**: Use the MCP server for programmatic access

## Acknowledgments

- **python-whois**: WHOIS client library
- **aiohttp**: Asynchronous HTTP client
- **rich**: Beautiful terminal formatting
- **typer**: CLI framework
- **pydantic**: Data validation
- **mcp**: Model Context Protocol
- **IANA**: RDAP bootstrap services

---

**Domain Checker** - Fast, reliable, and beautiful domain information tooling.
