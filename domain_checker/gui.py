"""
Domain Checker GUI - User-friendly textual interface
"""

import asyncio
from typing import List, Optional
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Button, Header, Footer, Input, Label, Static, 
    DataTable, Select, TextArea, TabbedContent, TabPane,
    LoadingIndicator, ProgressBar, Checkbox
)
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.reactive import reactive
from textual import events
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.console import Console
from rich import box
import json
from datetime import datetime
from pathlib import Path

from .core import DomainChecker
from .models import LookupResult, BulkLookupResult
from .cli import parse_dig_records


class LoadingScreen(ModalScreen):
    """Loading screen with progress indicator"""
    
    def __init__(self, message: str = "Loading..."):
        super().__init__()
        self.message = message
    
    def compose(self) -> ComposeResult:
        with Container(id="loading-container"):
            yield Static(self.message, id="loading-message")
            yield LoadingIndicator(id="loading-spinner")


class DomainLookupScreen(Screen):
    """Main domain lookup screen"""
    
    def __init__(self):
        super().__init__()
        self.checker = DomainChecker()
        self.current_result: Optional[LookupResult] = None
    
    def compose(self) -> ComposeResult:
        with Container(id="lookup-container"):
            # Header
            yield Static("🔍 Domain Lookup", id="screen-title")
            
            # Input section
            with Container(id="input-section"):
                yield Label("Enter domain name:", id="domain-label")
                yield Input(
                    placeholder="example.com",
                    id="domain-input"
                )
                
                # Method selection
                with Horizontal(id="method-container"):
                    yield Label("Method:", id="method-label")
                    yield Select(
                        options=[
                            ("Auto (Recommended)", "auto"),
                            ("WHOIS", "whois"),
                            ("RDAP", "rdap"),
                            ("DIG (DNS)", "dig")
                        ],
                        value="auto",
                        id="method-select"
                    )
                
                # DIG record type (only shown for DIG method)
                with Horizontal(id="dig-container", classes="hidden"):
                    yield Label("Record Type:", id="dig-label")
                    yield Select(
                        options=[
                            ("ANY (All records)", "ANY"),
                            ("A (IPv4)", "A"),
                            ("AAAA (IPv6)", "AAAA"),
                            ("MX (Mail)", "MX"),
                            ("NS (Name servers)", "NS"),
                            ("TXT (Text)", "TXT"),
                            ("SOA (Start of authority)", "SOA")
                        ],
                        value="ANY",
                        id="dig-select"
                    )
                
                # Lookup button
                yield Button("🔍 Lookup Domain", id="lookup-button", variant="primary")
            
            # Results section
            with ScrollableContainer(id="results-container"):
                yield Static("Results will appear here...", id="results-display")


class BulkLookupScreen(Screen):
    """Bulk domain lookup screen"""
    
    def __init__(self):
        super().__init__()
        self.checker = DomainChecker()
        self.results: List[LookupResult] = []
    
    def compose(self) -> ComposeResult:
        with Container(id="bulk-container"):
            # Header
            yield Static("📋 Bulk Domain Check", id="screen-title")
            
            # Input section
            with Container(id="input-section"):
                yield Label("Enter domains (one per line):", id="domains-label")
                yield TextArea(
                    placeholder="example.com\ngoogle.com\ngithub.com",
                    id="domains-input"
                )
                
                # Options
                with Horizontal(id="options-container"):
                    yield Label("Method:", id="method-label")
                    yield Select(
                        options=[
                            ("Auto (Recommended)", "auto"),
                            ("WHOIS", "whois"),
                            ("RDAP", "rdap"),
                            ("DIG (DNS)", "dig")
                        ],
                        value="auto",
                        id="method-select"
                    )
                
                with Horizontal(id="settings-container"):
                    yield Checkbox("Show progress", value=True, id="show-progress")
                    yield Label("Max concurrent:", id="concurrent-label")
                    yield Input(
                        value="10",
                        placeholder="10",
                        id="concurrent-input"
                    )
                
                # Buttons
                with Horizontal(id="button-container"):
                    yield Button("📋 Check Domains", id="bulk-button", variant="primary")
                    yield Button("📁 Load from File", id="load-file-button")
                    yield Button("💾 Save Results", id="save-results-button")
            
            # Results section
            with Container(id="results-section"):
                yield DataTable(id="results-table")
                yield Static("", id="summary-display")


class SettingsScreen(Screen):
    """Settings and preferences screen"""
    
    def compose(self) -> ComposeResult:
        with Container(id="settings-container"):
            # Header
            yield Static("⚙️ Settings", id="screen-title")
            
            # Settings sections
            with TabbedContent(id="settings-tabs"):
                with TabPane("General", id="general-tab"):
                    with Container(id="general-settings"):
                        yield Label("Default lookup method:", id="default-method-label")
                        yield Select(
                            options=[
                                ("Auto (Recommended)", "auto"),
                                ("WHOIS", "whois"),
                                ("RDAP", "rdap"),
                                ("DIG (DNS)", "dig")
                            ],
                            value="auto",
                            id="default-method-select"
                        )
                        
                        yield Label("Default timeout (seconds):", id="timeout-label")
                        yield Input(
                            value="30",
                            placeholder="30",
                            id="timeout-input"
                        )
                        
                        yield Label("Default concurrent lookups:", id="concurrent-label")
                        yield Input(
                            value="10",
                            placeholder="10",
                            id="concurrent-input"
                        )
                
                with TabPane("Display", id="display-tab"):
                    with Container(id="display-settings"):
                        yield Checkbox("Show emojis in results", value=True, id="show-emojis")
                        yield Checkbox("Show raw data", value=False, id="show-raw")
                        yield Checkbox("Auto-scroll results", value=True, id="auto-scroll")
                        yield Checkbox("Colorize output", value=True, id="colorize")
                
                with TabPane("Advanced", id="advanced-tab"):
                    with Container(id="advanced-settings"):
                        yield Label("Rate limit (requests/second):", id="rate-limit-label")
                        yield Input(
                            value="1.0",
                            placeholder="1.0",
                            id="rate-limit-input"
                        )
                        
                        yield Label("User agent:", id="user-agent-label")
                        yield Input(
                            value="Domain-Checker/1.3.1",
                            placeholder="Domain-Checker/1.3.1",
                            id="user-agent-input"
                        )
            
            # Save button
            yield Button("💾 Save Settings", id="save-settings-button", variant="primary")


class HelpScreen(Screen):
    """Help and documentation screen"""
    
    def compose(self) -> ComposeResult:
        with Container(id="help-container"):
            # Header
            yield Static("❓ Help & Documentation", id="screen-title")
            
            # Help content
            with TabbedContent(id="help-tabs"):
                with TabPane("Getting Started", id="getting-started-tab"):
                    with ScrollableContainer(id="getting-started-content"):
                        yield Static("""
# Getting Started with Domain Checker

## What is Domain Checker?
Domain Checker is a powerful tool for looking up domain information including:
- Domain registration details
- Name servers
- Contact information
- DNS records
- Domain availability

## How to Use

### Single Domain Lookup
1. Go to the "Domain Lookup" tab
2. Enter a domain name (e.g., example.com)
3. Select a lookup method (Auto is recommended)
4. Click "Lookup Domain"

### Bulk Domain Check
1. Go to the "Bulk Check" tab
2. Enter multiple domains (one per line)
3. Configure settings as needed
4. Click "Check Domains"

### Understanding Results
- ✅ Green: Domain is registered and active
- ❌ Red: Domain is not registered or has issues
- ⚠️ Yellow: Domain status is unclear

## Tips
- Use "Auto" method for best results
- WHOIS provides detailed registration info
- RDAP is faster and more structured
- DIG shows DNS records and technical details
                        """, id="getting-started-text")
                
                with TabPane("Methods", id="methods-tab"):
                    with ScrollableContainer(id="methods-content"):
                        yield Static("""
# Lookup Methods Explained

## Auto (Recommended)
- Tries RDAP first, falls back to WHOIS
- Best balance of speed and information
- Works for most domains

## WHOIS
- Traditional domain lookup protocol
- Provides detailed registration information
- Includes contact details (when available)
- Slower but more comprehensive

## RDAP
- Modern replacement for WHOIS
- Faster and more structured
- Better error handling
- Limited contact information

## DIG (DNS)
- Shows DNS records and technical details
- Includes A, AAAA, MX, NS, TXT records
- Useful for troubleshooting DNS issues
- No registration information

## When to Use Each Method

### Use Auto when:
- You want the best overall experience
- You're not sure which method to use
- You need both registration and DNS info

### Use WHOIS when:
- You need detailed contact information
- You're checking domain availability
- You need comprehensive registration details

### Use RDAP when:
- You want fast lookups
- You need structured data
- You're doing bulk operations

### Use DIG when:
- You're troubleshooting DNS issues
- You need to see all DNS records
- You want to check name server configuration
                        """, id="methods-text")
                
                with TabPane("Troubleshooting", id="troubleshooting-tab"):
                    with ScrollableContainer(id="troubleshooting-content"):
                        yield Static("""
# Troubleshooting Common Issues

## "Domain not found" or "No match"
- The domain is likely not registered
- Try a different lookup method
- Check if you typed the domain correctly

## "Connection timeout"
- Network connectivity issues
- Try again in a few moments
- Check your internet connection

## "Rate limited"
- Too many requests too quickly
- Wait a moment before trying again
- Reduce concurrent lookups in settings

## "Permission denied"
- Some registrars block automated lookups
- Try a different method (WHOIS vs RDAP)
- Use DIG for DNS-only information

## Slow lookups
- WHOIS is generally slower than RDAP
- Try reducing concurrent lookups
- Check your internet connection speed

## No contact information
- Many domains hide contact info for privacy
- This is normal and expected
- GDPR regulations limit contact data

## Getting help
- Check the official documentation
- Visit the GitHub repository
- Report issues with detailed error messages
                        """, id="troubleshooting-text")


class AboutScreen(Screen):
    """About and version information screen"""
    
    def compose(self) -> ComposeResult:
        with Container(id="about-container"):
            # Header
            yield Static("ℹ️ About Domain Checker", id="screen-title")
            
            # About content
            with ScrollableContainer(id="about-content"):
                yield Static("""
# Domain Checker v1.3.1

A powerful, user-friendly domain lookup tool with support for WHOIS, RDAP, and DNS lookups.

## Features
- 🔍 Single domain lookups
- 📋 Bulk domain checking
- 🌐 Multiple lookup methods (WHOIS, RDAP, DIG)
- 📊 Beautiful, easy-to-use interface
- ⚡ Fast asynchronous processing
- 💾 Export results to various formats
- 🎨 Rich, colorful output

## Created by
**Zac Roach**

## License
MIT License - Free to use and modify

## Repository
https://github.com/TheZacillac/domain-checker

## Technical Details
- Built with Python 3.8+
- Uses asyncio for fast concurrent lookups
- Rich terminal interface with Textual
- Supports WHOIS, RDAP, and DNS protocols
- Rate limiting and error handling

## Acknowledgments
- Thanks to all contributors and users
- Built with open source tools and libraries
- Community feedback and suggestions welcome

## Version History
- v1.3.1: Fixed updater, improved force updates
- v1.3.0: Added multiple output formats (Plain, JSON, CSV)
- v1.2.0: Performance optimizations and about command
- v1.1.0: Comprehensive documentation and examples
- v1.0.0: Initial release with core functionality

## Support
For issues, questions, or suggestions:
- Create an issue on GitHub
- Check the documentation
- Review the help section in this app
                """, id="about-text")


class DomainCheckerGUI(App):
    """Main Domain Checker GUI application"""
    
    CSS = """
    #main-container {
        layout: vertical;
        height: 100%;
    }
    
    #screen-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 1;
    }
    
    #input-section {
        height: auto;
        margin: 1;
        padding: 1;
        border: solid $primary;
    }
    
    #results-container {
        height: 1fr;
        margin: 1;
        padding: 1;
        border: solid $secondary;
    }
    
    #results-display {
        height: auto;
        min-height: 10;
    }
    
    #lookup-button, #bulk-button, #save-settings-button {
        margin: 1;
    }
    
    #domain-input, #domains-input {
        margin: 1;
    }
    
    #method-container, #dig-container, #options-container, #settings-container {
        height: auto;
        margin: 1;
    }
    
    #method-label, #dig-label, #concurrent-label {
        width: 15;
        margin-right: 1;
    }
    
    #method-select, #dig-select {
        width: 20;
    }
    
    #results-table {
        height: 1fr;
    }
    
    #summary-display {
        height: auto;
        margin-top: 1;
    }
    
    .hidden {
        display: none;
    }
    
    .success {
        color: $success;
    }
    
    .error {
        color: $error;
    }
    
    .warning {
        color: $warning;
    }
    
    .info {
        color: $primary;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("f1", "help", "Help"),
        Binding("ctrl+h", "help", "Help"),
    ]
    
    def __init__(self):
        super().__init__()
        self.checker = DomainChecker()
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app"""
        yield Header()
        
        with Container(id="main-container"):
            with TabbedContent(id="main-tabs"):
                with TabPane("🔍 Domain Lookup", id="lookup-tab"):
                    yield DomainLookupScreen()
                
                with TabPane("📋 Bulk Check", id="bulk-tab"):
                    yield BulkLookupScreen()
                
                with TabPane("⚙️ Settings", id="settings-tab"):
                    yield SettingsScreen()
                
                with TabPane("❓ Help", id="help-tab"):
                    yield HelpScreen()
                
                with TabPane("ℹ️ About", id="about-tab"):
                    yield AboutScreen()
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app starts"""
        self.title = "Domain Checker v1.3.1"
        self.sub_title = "User-Friendly Domain Lookup Tool"
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        if event.input.id == "domain-input":
            self.action_lookup_domain()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes"""
        if event.select.id == "method-select":
            # Show/hide DIG options based on method
            dig_container = self.query_one("#dig-container")
            if event.value == "dig":
                dig_container.remove_class("hidden")
            else:
                dig_container.add_class("hidden")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "lookup-button":
            self.action_lookup_domain()
        elif event.button.id == "bulk-button":
            self.action_bulk_lookup()
        elif event.button.id == "load-file-button":
            self.action_load_file()
        elif event.button.id == "save-results-button":
            self.action_save_results()
        elif event.button.id == "save-settings-button":
            self.action_save_settings()
    
    def action_lookup_domain(self) -> None:
        """Perform single domain lookup"""
        domain_input = self.query_one("#domain-input")
        method_select = self.query_one("#method-select")
        dig_select = self.query_one("#dig-select")
        results_display = self.query_one("#results-display")
        
        domain = domain_input.value.strip()
        if not domain:
            results_display.update("❌ Please enter a domain name")
            return
        
        method = method_select.value
        dig_record_type = dig_select.value if method == "dig" else "ANY"
        
        # Show loading
        results_display.update("🔄 Looking up domain...")
        
        # Perform lookup asynchronously
        self.set_timer(0.1, lambda: self._do_lookup(domain, method, dig_record_type))
    
    async def _do_lookup(self, domain: str, method: str, dig_record_type: str) -> None:
        """Perform the actual domain lookup"""
        try:
            result = await self.checker.lookup_domain(domain, method, dig_record_type)
            self._display_lookup_result(result)
        except Exception as e:
            results_display = self.query_one("#results-display")
            results_display.update(f"❌ Error: {str(e)}")
    
    def _display_lookup_result(self, result: LookupResult) -> None:
        """Display lookup result in a user-friendly format"""
        results_display = self.query_one("#results-display")
        
        if not result.success or not result.data:
            results_display.update(f"❌ Failed to lookup {result.domain}\nError: {result.error}")
            return
        
        domain_info = result.data
        is_dig = result.method.lower() == 'dig'
        
        # Create result text
        result_text = f"✅ Domain: {domain_info.domain}\n"
        result_text += f"🔧 Method: {result.method.upper()}\n"
        result_text += f"⏱️ Lookup Time: {result.lookup_time:.2f}s\n\n"
        
        if not is_dig:
            result_text += f"🏢 Registrar: {domain_info.registrar or 'N/A'}\n"
            result_text += f"📊 Status: {', '.join(domain_info.status) if domain_info.status else 'N/A'}\n\n"
        
        # Name servers
        if domain_info.name_servers:
            result_text += "🌐 Name Servers:\n"
            for ns in domain_info.name_servers:
                result_text += f"  • {ns}\n"
            result_text += "\n"
        
        # For DIG lookups, show resolved records
        if is_dig and domain_info.raw_data:
            parsed_records = parse_dig_records(domain_info.raw_data, domain_info.domain)
            if parsed_records:
                result_text += "📋 DNS Records:\n"
                result_text += "Type     Name                      Target                                    TTL\n"
                result_text += "-" * 80 + "\n"
                for record in parsed_records:
                    name = record["name"] if record["name"] else "N/A"
                    ttl = record["ttl"] if record["ttl"] else "N/A"
                    result_text += f"{record['type']:<8} {name:<25} {record['target']:<40} {ttl}\n"
                result_text += "\n"
            else:
                # Fallback to simple display if parsing fails
                records = [line.strip() for line in domain_info.raw_data.strip().split('\n') if line.strip()]
                if records:
                    result_text += "📋 DNS Records:\n"
                    for record in records:
                        result_text += f"  • {record}\n"
                    result_text += "\n"
        
        # Dates (skip for DIG)
        if not is_dig:
            result_text += "📅 Important Dates:\n"
            result_text += f"  • Creation: {self._format_date(domain_info.creation_date)}\n"
            result_text += f"  • Expiration: {self._format_date(domain_info.expiration_date)}\n"
            result_text += f"  • Last Updated: {self._format_date(domain_info.updated_date)}\n\n"
        
        # Contacts (skip for DIG)
        if not is_dig:
            has_contacts = (
                domain_info.registrant or 
                domain_info.admin_contact or 
                domain_info.tech_contact
            )
            
            if has_contacts:
                result_text += "👤 Contact Information:\n"
                if domain_info.registrant:
                    result_text += f"  • Registrant: {self._format_contact(domain_info.registrant)}\n"
                if domain_info.admin_contact:
                    result_text += f"  • Admin: {self._format_contact(domain_info.admin_contact)}\n"
                if domain_info.tech_contact:
                    result_text += f"  • Technical: {self._format_contact(domain_info.tech_contact)}\n"
        
        results_display.update(result_text)
    
    def _format_date(self, date) -> str:
        """Format datetime for display"""
        if not date:
            return "N/A"
        return date.strftime("%Y-%m-%d %H:%M:%S")
    
    def _format_contact(self, contact) -> str:
        """Format contact information for display"""
        if not contact:
            return "N/A"
        
        parts = []
        if contact.get('name') or contact.get('fn'):
            parts.append(f"Name: {contact.get('name') or contact.get('fn')}")
        if contact.get('email'):
            parts.append(f"Email: {contact['email']}")
        if contact.get('organization'):
            parts.append(f"Org: {contact['organization']}")
        
        return ", ".join(parts) if parts else "N/A"
    
    def action_bulk_lookup(self) -> None:
        """Perform bulk domain lookup"""
        domains_input = self.query_one("#domains-input")
        method_select = self.query_one("#method-select")
        concurrent_input = self.query_one("#concurrent-input")
        results_table = self.query_one("#results-table")
        summary_display = self.query_one("#summary-display")
        
        domains_text = domains_input.text.strip()
        if not domains_text:
            summary_display.update("❌ Please enter at least one domain")
            return
        
        domains = [d.strip() for d in domains_text.split('\n') if d.strip()]
        if not domains:
            summary_display.update("❌ No valid domains found")
            return
        
        method = method_select.value
        try:
            max_concurrent = int(concurrent_input.value)
        except ValueError:
            max_concurrent = 10
        
        # Clear previous results
        results_table.clear()
        results_table.add_columns("Domain", "Status", "Method", "Time", "Registrar")
        
        # Show loading
        summary_display.update(f"🔄 Checking {len(domains)} domains...")
        
        # Perform bulk lookup asynchronously
        self.set_timer(0.1, lambda: self._do_bulk_lookup(domains, method, max_concurrent))
    
    async def _do_bulk_lookup(self, domains: List[str], method: str, max_concurrent: int) -> None:
        """Perform the actual bulk lookup"""
        try:
            # Update checker settings
            self.checker.max_concurrent = max_concurrent
            
            results = await self.checker.lookup_domains_bulk(domains, method)
            self._display_bulk_results(results)
        except Exception as e:
            summary_display = self.query_one("#summary-display")
            summary_display.update(f"❌ Error: {str(e)}")
    
    def _display_bulk_results(self, results: BulkLookupResult) -> None:
        """Display bulk lookup results"""
        results_table = self.query_one("#results-table")
        summary_display = self.query_one("#summary-display")
        
        # Clear and setup table
        results_table.clear()
        results_table.add_columns("Domain", "Status", "Method", "Time", "Registrar")
        
        # Add results to table
        for result in results.results:
            if result.registration_status == "registered":
                status = "✅ Registered"
            elif result.registration_status == "not_registered":
                status = "❌ Not Registered"
            elif result.registration_status == "possibly_registered":
                status = "⚠️ Possibly Registered"
            else:
                status = "✅ Success" if result.success else "❌ Failed"
            
            method = result.method.upper() if result.method else "N/A"
            time_str = f"{result.lookup_time:.2f}s"
            registrar = result.data.registrar if result.data and result.data.registrar else "N/A"
            
            results_table.add_row(
                result.domain,
                status,
                method,
                time_str,
                registrar
            )
        
        # Update summary
        registered_count = sum(1 for r in results.results if r.registration_status == "registered")
        not_registered_count = sum(1 for r in results.results if r.registration_status == "not_registered")
        possibly_registered_count = sum(1 for r in results.results if r.registration_status == "possibly_registered")
        
        summary_text = f"""
📊 Bulk Lookup Complete!

Total Domains: {results.total_domains}
✅ Registered: {registered_count}
❌ Not Registered: {not_registered_count}
⚠️ Possibly Registered: {possibly_registered_count}
⏱️ Total Time: {results.total_time:.2f}s
📈 Average per Domain: {results.average_time_per_domain:.2f}s
        """.strip()
        
        summary_display.update(summary_text)
    
    def action_load_file(self) -> None:
        """Load domains from file"""
        # This would open a file dialog in a real implementation
        # For now, show a message
        summary_display = self.query_one("#summary-display")
        summary_display.update("📁 File loading not implemented in this version")
    
    def action_save_results(self) -> None:
        """Save results to file"""
        # This would save results to a file
        summary_display = self.query_one("#summary-display")
        summary_display.update("💾 Result saving not implemented in this version")
    
    def action_save_settings(self) -> None:
        """Save settings"""
        # This would save settings to a config file
        # For now, show a message
        summary_display = self.query_one("#summary-display")
        summary_display.update("💾 Settings saved! (Note: Settings persistence not implemented in this version)")
    
    def action_help(self) -> None:
        """Show help"""
        # Switch to help tab
        main_tabs = self.query_one("#main-tabs")
        main_tabs.active = "help-tab"
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def run_gui():
    """Run the Domain Checker GUI"""
    app = DomainCheckerGUI()
    app.run()


if __name__ == "__main__":
    run_gui()
