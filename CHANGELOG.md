# Changelog

All notable changes to the Domain Checker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-10-19

### Added
- Dedicated "Resolved Records" box for DIG lookups
- Clean, formatted panel display for DNS query results
- Bullet-pointed records with color coding (cyan bullets, yellow text)

### Changed
- DIG display now shows resolved records in a dedicated green-bordered panel
- Removed "Raw Data" section from DIG output to avoid duplication
- Improved visual hierarchy: Domain Info → Resolved Records → Name Servers (if NS query)
- Simplified DIG info panel to show only Domain, Method, and Lookup Time

### Improved
- Better readability for DNS lookups
- Professional formatting for all DIG record types (A, AAAA, MX, NS, TXT, etc.)
- Consistent visual design across all lookup methods

## [1.0.2] - 2025-10-19

### Added
- Full contact information display (name, organization, email, phone, address)
- Multi-line contact formatting with icons (📧 📞 📍)
- Enhanced contact table with row separation
- Test script for demonstrating full contact display (`test_contact_display.py`)
- Comprehensive documentation (`CONTACT_INFORMATION.md`)

### Changed
- Improved `format_contact()` function to show all available fields
- Updated contact table layout with `show_lines=True` for better readability
- Enhanced vCard parsing to store both `'fn'` and `'name'` fields

### Documentation
- Added CONTACT_INFORMATION.md explaining display features and privacy considerations
- Updated documentation about GDPR compliance and why contact info is often hidden

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

[1.0.3]: https://github.com/yourusername/domain-checker/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/yourusername/domain-checker/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/yourusername/domain-checker/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/yourusername/domain-checker/releases/tag/v1.0.0

