# Changelog

All notable changes to the Domain Checker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-10-19

### Added
- Integrated TheZacillac/rdap-cli framework for RDAP lookups
- IANA Bootstrap Service discovery for automatic RDAP server selection
- Support for TLD-specific RDAP server routing
- Improved vCard parsing for contact information
- Added RDAP_FRAMEWORK.md documentation

### Changed
- RDAP client now uses official IANA bootstrap files
- Updated RDAP queries to use proper RFC 7480-7485 protocol
- Enhanced RDAP response parsing with better structured data extraction

### Fixed
- SSL certificate verification issues with RDAP servers
- Improved error handling for RDAP queries

## [1.0.0] - 2025-10-19

### Added
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

### Features
- **Triple Protocol Support**: WHOIS, RDAP, and DIG
- **DNS Propagation**: Check resolution across global DNS resolvers
- **Async/Concurrent**: Fast parallel lookups with rate limiting
- **Beautiful Output**: Rich CLI with tables, panels, and colors
- **MCP Integration**: Connect via Model Context Protocol
- **Extensible**: Easy to add new lookup methods

### Documentation
- Comprehensive README with usage examples
- Installation guide (INSTALLATION.md)
- Example scripts for basic, advanced, DIG, and propagation use cases
- API documentation
- Configuration guide

[1.0.1]: https://github.com/yourusername/domain-checker/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/yourusername/domain-checker/releases/tag/v1.0.0

