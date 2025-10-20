# Changelog

All notable changes to the Domain Checker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.7] - 2025-10-19

### Changed
- Updated DNS propagation command from `propagation` to `prop` for improved usability
- Shorter, more convenient command name (4 characters vs 12 characters)
- Updated documentation to use new `prop` command name
- Improved command-line ergonomics for DNS propagation checking

### Fixed
- All DNS propagation functionality preserved with new command name
- Complete documentation updates for the new command

## [1.0.6] - 2025-10-19

### Changed
- Updated CLI command name from `domain-check` to `domch` for improved usability
- Shorter, more convenient command name (5 characters vs 12 characters)
- Updated all documentation and examples to use new command name
- Improved command-line ergonomics and typing efficiency

### Removed
- Legacy `domain-check` command (breaking change for existing users)
- Users must update scripts and aliases to use `domch` command

### Fixed
- All CLI functionality preserved with new command name
- Complete documentation updates across all files
- Package reinstallation required to access new command

## [1.0.5] - 2025-10-19

### Added
- Enhanced bulk domain checking with meaningful registration status
- Three distinct registration statuses: "registered", "not_registered", "possibly_registered"
- Smart registration status detection based on domain information, error messages, and raw data
- Updated bulk results display with registration status counts and emoji indicators

### Changed
- Bulk lookup results now show "Registration Status" instead of generic "Success/Failed"
- Summary panel displays counts for each registration status type
- Results table uses intuitive status indicators (✅ Registered, ❌ Not Registered, ⚠️ Possibly Registered)
- Enhanced registration detection patterns for better accuracy

### Fixed
- Improved detection of non-registered domains with "no whois data available" messages
- Better handling of various "not found" error patterns across different WHOIS servers
- More accurate registration status determination for edge cases

## [1.0.4] - 2025-10-19

### Added
- Comprehensive DIG ANY record support - now returns ALL DNS record types
- Multi-record type queries for complete domain analysis
- Organized output with section headers for each record type (A, AAAA, MX, NS, SOA, TXT, CNAME)
- Enhanced DNS information coverage including IPv6, mail servers, and verification records

### Changed
- DIG ANY queries now perform multiple record type lookups instead of single query
- Improved DIG output format with clear section separation
- Enhanced MCP server with updated DIG functionality
- Better error handling for failed record type queries

### Fixed
- DIG ANY queries now return comprehensive DNS information instead of single A record
- Resolved DNS server blocking issues with ANY queries by using multiple specific queries

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

