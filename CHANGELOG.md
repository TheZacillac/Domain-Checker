# Changelog

All notable changes to the Domain Checker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.2] - 2025-01-27

### Added
- **User-Friendly GUI**: Complete graphical interface using Textual framework
- **GUI Command**: New `domch gui` command to launch the graphical interface
- **Tabbed Interface**: Domain Lookup, Bulk Check, Settings, Help, and About tabs
- **Form-Based Input**: Easy-to-use forms for domain entry and configuration
- **Real-Time Results**: Live results display with emojis and formatting
- **Built-in Help**: Integrated documentation and troubleshooting guides
- **Settings Management**: GUI-based configuration without editing files
- **Keyboard Navigation**: Full keyboard support with shortcuts
- **Visual Feedback**: Emojis, colors, and status indicators for easy understanding

### Features
- **Domain Lookup Tab**: Simple form for single domain lookups with method selection
- **Bulk Check Tab**: Multi-domain checking with results table and summary
- **Settings Tab**: General, Display, and Advanced configuration options
- **Help Tab**: Getting Started, Methods explanation, and Troubleshooting guides
- **About Tab**: Version info, features, credits, and repository links
- **No CLI Knowledge Required**: Perfect for non-technical users
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Changed
- Updated CLI help to mention GUI option
- Enhanced about command to show GUI usage
- Updated README with comprehensive GUI documentation
- Added Textual dependency for GUI framework

## [1.3.1] - 2025-01-27

### Fixed
- **Update Command**: Fixed updater not pulling latest files from GitHub
- Force update now explicitly pulls from main branch with git fetch/reset
- Added commit hash verification to show exactly what was pulled
- Improved force update messaging to show it's pulling latest main branch
- Fixed version comparison logic when local version is newer than releases
- Update now displays commit hash, message, and date of pulled code

### Changed
- Force update bypasses version checks completely and always pulls latest
- Updater now explicitly targets main branch with `--single-branch`
- Added git fetch + reset when force flag is used for absolute latest
- Better user feedback showing which commit was pulled during update

## [1.3.0] - 2025-01-27

### Added
- **Multiple Output Formats**: Support for Rich, Plain, JSON, and CSV output formats
- **Plain Text Output**: Clean, copy/paste friendly output without formatting, colors, or emojis
- **JSON Output**: Structured JSON output for programmatic use and integration with other tools
- **CSV Output**: Comma-separated values format for bulk operations (Excel/spreadsheet import)
- **Format Flag**: New `--format` (or `-f`) option for all major commands
- **Format Support**: Output format support for `lookup`, `bulk`, `file`, `dig`, `reverse`, and `prop` commands
- **Documentation**: Comprehensive output format documentation section in README
- **Examples**: New EXAMPLES_OUTPUT_FORMATS.md with detailed use cases
- **Test Script**: test_output_formats.py for demonstrating the new features

### Changed
- CLI commands now accept `--format` flag to specify output format
- Progress bars and rich formatting only shown for `rich` format
- Bulk and file commands now support CSV export for spreadsheet integration
- Updated all command help text to indicate format support
- Enhanced documentation with format comparison tables and use cases

### Features
- **Copy/Paste Friendly**: Plain format removes all Rich markup, making output easy to copy
- **Programmatic Integration**: JSON format enables seamless integration with scripts and tools
- **Excel Integration**: CSV format allows direct import into Excel and Google Sheets
- **Backwards Compatible**: Default format remains `rich` for existing users
- **Format-Specific Display**: Each format optimized for its use case

### Use Cases
- Copy name servers without formatting: `domch lookup example.com --format plain`
- Extract registrar with jq: `domch lookup example.com --format json | jq '.data.registrar'`
- Export to Excel: `domch file domains.txt --format csv > results.csv`
- Script integration: `domch bulk domain1.com domain2.com --format json`

## [1.2.0] - 2025-01-27

### Added
- New `about` command to display version information and credits
- Comprehensive performance optimizations for faster domain lookups

### Changed
- **Performance Improvements**: Significantly faster domain lookups through multiple optimizations
- **Rate Limiting**: DIG operations now bypass throttling for local DNS queries (3x faster)
- **Parallel Processing**: DIG ANY record lookups now run in parallel instead of sequential
- **Connection Pooling**: RDAP client now uses aiohttp with keep-alive connections
- **Static Config**: RDAP server discovery now uses static config map first, reducing bootstrap downloads
- **Multi-record DIG**: Multiple record type lookups now run concurrently

### Performance Gains
- **DIG Operations**: ~3x faster (0.03s per domain vs 0.1s+ previously)
- **DIG ANY Records**: ~2x faster through parallel record type queries
- **RDAP Lookups**: ~30% faster through connection pooling and static config
- **Bulk Operations**: Significantly improved throughput for large domain lists

### Technical Details
- Replaced urllib with aiohttp for RDAP connections
- Implemented asyncio.gather for parallel DIG record queries
- Added static TLD-to-RDAP-server mapping to avoid bootstrap downloads
- Optimized throttling to only apply to HTTP-based operations

## [1.1.0] - 2025-01-27

### Added
- Comprehensive examples and documentation consolidated into README.md
- Complete installation guide with pipx as primary method
- Advanced usage examples including performance benchmarking
- MCP server usage examples
- Troubleshooting guide with common issues and solutions

### Changed
- Updated installation instructions to prioritize pipx over pip
- Streamlined project structure by removing unnecessary files
- Enhanced README with all functionality examples and documentation
- Improved installation experience with better error handling guidance

### Removed
- Backup directory and build artifacts
- Separate examples directory (consolidated into README)
- Test files (can be created dynamically when needed)
- Installation and build scripts (simplified to pipx/pip only)
- Rust components for simpler maintenance
- Separate documentation files (consolidated into README)

### Fixed
- Project bloat reduced significantly while maintaining all functionality
- Single source of truth for all documentation and examples
- Simplified installation process with pipx as primary method

## [1.0.8] - 2025-10-19

### Added
- Comprehensive consolidated documentation in `DOCUMENTATION.md`
- Complete documentation covering installation, usage, API reference, examples, and troubleshooting
- Table of contents for easy navigation through all documentation sections

### Changed
- Consolidated 20+ separate documentation files into single comprehensive `DOCUMENTATION.md`
- Updated README.md to point to consolidated documentation
- Improved documentation organization and structure

### Removed
- Redundant documentation files that were consolidated:
  - `INSTALLATION.md`, `PROJECT_SUMMARY.md`, `CHANGES_SUMMARY.md`
  - `COMMAND_NAME_CHANGE.md`, `CONTACT_INFORMATION.md`
  - `DIG_ANY_UPDATE.md`, `DIG_DISPLAY_UPDATE.md`, `DIG_FEATURE_SUMMARY.md`
  - `DNS_PROPAGATION_FEATURE.md`, `FINAL_SUMMARY.md`
  - `MCP_SERVER_UPDATE.md`, `PERFORMANCE_IMPROVEMENTS_SUMMARY.md`
  - `PERFORMANCE_OPTIMIZATION_PLAN.md`, `RDAP_FRAMEWORK.md`
  - `REGISTRATION_STATUS_UPDATE.md`, `RESOLVED_RECORDS_DISPLAY.md`
  - `SPEED_OPTIMIZATIONS_FINAL.md`, `STREAMLINED_UPDATE.md`
  - `UPDATER_DOCUMENTATION.md`, `UPDATER_SUMMARY.md`

### Fixed
- Documentation maintenance complexity reduced from 20+ files to 3 files
- Single source of truth for all project documentation
- Better user experience with consolidated, well-organized documentation

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

