"""
Command-line interface for domain checker
"""

import asyncio
import typer
from typing import List, Optional, Dict
from pathlib import Path
import json
import csv
from io import StringIO
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich.syntax import Syntax
from rich import box
from datetime import datetime

from .core import DomainChecker
from .models import LookupResult, BulkLookupResult
from .updater import DomainCheckerUpdater

app = typer.Typer(
    name="domch",
    help="Asynchronous domain checker with WHOIS and RDAP support",
    add_completion=False,
    rich_markup_mode="rich"
)
console = Console()


def format_date_plain(date: Optional[datetime]) -> str:
    """Format datetime for plain text display"""
    if not date:
        return "N/A"
    return date.strftime("%Y-%m-%d %H:%M:%S")


def format_contact_plain(contact: Optional[dict]) -> str:
    """Format contact information for plain text display"""
    if not contact:
        return "N/A"
    
    parts = []
    
    # Name
    if contact.get('name') or contact.get('fn'):
        parts.append(f"Name: {contact.get('name') or contact.get('fn')}")
    
    # Organization
    if contact.get('organization'):
        parts.append(f"Organization: {contact['organization']}")
    
    # Email
    if contact.get('email'):
        parts.append(f"Email: {contact['email']}")
    
    # Phone
    if contact.get('phone'):
        parts.append(f"Phone: {contact['phone']}")
    
    # Address
    if contact.get('address'):
        parts.append(f"Address: {contact['address']}")
    
    return ", ".join(parts) if parts else "N/A"


def display_domain_info_plain(result: LookupResult, show_raw: bool = False):
    """Display domain information in plain text format with color coding"""
    if not result.success or not result.data:
        print(f"Failed to lookup {result.domain}")
        if result.error:
            print(f"Error: {result.error}")
        return
    
    domain_info = result.data
    is_dig = result.method.lower() == 'dig'
    
    print("Domain Information")
    print("Domain: " + domain_info.domain)
    print("Method: " + result.method.upper())
    print("Lookup Time: " + f"{result.lookup_time:.2f}s")
    
    if not is_dig:
        print("Registrar: " + (domain_info.registrar or "N/A"))
        status = ", ".join(domain_info.status) if domain_info.status else "N/A"
        print("Status: " + status)
    
    # Name servers
    if domain_info.name_servers:
        print("Name Servers:")
        for ns in domain_info.name_servers:
            print("  " + ns)
    
    # For DIG lookups, show resolved records
    if is_dig and domain_info.raw_data:
        parsed_records = parse_dig_records(domain_info.raw_data, domain_info.domain)
        if parsed_records:
            print("Resolved Records:")
            print("Type     Name                      Target                                    TTL")
            print("-" * 80)
            for record in parsed_records:
                name = record["name"] if record["name"] else "N/A"
                ttl = record["ttl"] if record["ttl"] else "N/A"
                print(f"{record['type']:<8} {name:<25} {record['target']:<40} {ttl}")
        else:
            # Fallback to simple display if parsing fails
            records = [line.strip() for line in domain_info.raw_data.strip().split('\n') if line.strip()]
            if records:
                print("Resolved Records:")
                for record in records:
                    print("  " + record)
    
    # Dates (skip for DIG)
    if not is_dig:
        print("Important Dates:")
        print("  Creation: " + format_date_plain(domain_info.creation_date))
        print("  Expiration: " + format_date_plain(domain_info.expiration_date))
        print("  Last Updated: " + format_date_plain(domain_info.updated_date))
    
    # Contacts (skip for DIG)
    if not is_dig:
        has_contacts = (
            domain_info.registrant or 
            domain_info.admin_contact or 
            domain_info.tech_contact
        )
        
        if has_contacts:
            print("Contact Information:")
            if domain_info.registrant:
                print("  Registrant: " + format_contact_plain(domain_info.registrant))
            if domain_info.admin_contact:
                print("  Admin: " + format_contact_plain(domain_info.admin_contact))
            if domain_info.tech_contact:
                print("  Technical: " + format_contact_plain(domain_info.tech_contact))
    
    # Show raw data if requested
    if show_raw and domain_info.raw_data:
        print("\nRaw Data:")
        print(domain_info.raw_data)


def display_domain_info_json(result: LookupResult, show_raw: bool = False):
    """Display domain information in JSON format"""
    data = {
        "domain": result.domain,
        "success": result.success,
        "method": result.method,
        "lookup_time": result.lookup_time,
        "registration_status": result.registration_status,
        "error": result.error
    }
    
    if result.data:
        data["data"] = {
            "domain": result.data.domain,
            "registrar": result.data.registrar,
            "creation_date": result.data.creation_date.isoformat() if result.data.creation_date else None,
            "expiration_date": result.data.expiration_date.isoformat() if result.data.expiration_date else None,
            "updated_date": result.data.updated_date.isoformat() if result.data.updated_date else None,
            "status": result.data.status,
            "name_servers": result.data.name_servers,
            "registrant": result.data.registrant,
            "admin_contact": result.data.admin_contact,
            "tech_contact": result.data.tech_contact,
            "source": result.data.source,
            "raw_data": result.data.raw_data if show_raw else None
        }
    
    print(json.dumps(data, indent=2))


def display_bulk_results_plain(results: BulkLookupResult):
    """Display bulk results in plain text format"""
    registered_count = sum(1 for r in results.results if r.registration_status == "registered")
    not_registered_count = sum(1 for r in results.results if r.registration_status == "not_registered")
    possibly_registered_count = sum(1 for r in results.results if r.registration_status == "possibly_registered")
    
    print("Bulk Lookup Summary")
    print("Total Domains: " + str(results.total_domains))
    print("Registered: " + str(registered_count))
    print("Not Registered: " + str(not_registered_count))
    print("Possibly Registered: " + str(possibly_registered_count))
    print("Total Time: " + f"{results.total_time:.2f}s")
    print("Average per Domain: " + f"{results.average_time_per_domain:.2f}s")
    print("")
    print("Domain\tStatus\tMethod\tTime\tRegistrar")
    
    for result in results.results:
        if result.registration_status == "registered":
            status = "Registered"
        elif result.registration_status == "not_registered":
            status = "Not Registered"
        elif result.registration_status == "possibly_registered":
            status = "Possibly Registered"
        else:
            status = "Success" if result.success else "Failed"
        
        method = result.method.upper() if result.method else "N/A"
        time_str = f"{result.lookup_time:.2f}s"
        registrar = result.data.registrar if result.data and result.data.registrar else "N/A"
        
        print(result.domain + "\t" + status + "\t" + method + "\t" + time_str + "\t" + registrar)


def display_bulk_results_json(results: BulkLookupResult):
    """Display bulk results in JSON format"""
    data = {
        "total_domains": results.total_domains,
        "successful_lookups": results.successful_lookups,
        "failed_lookups": results.failed_lookups,
        "total_time": results.total_time,
        "average_time_per_domain": results.average_time_per_domain,
        "results": []
    }
    
    for result in results.results:
        result_data = {
            "domain": result.domain,
            "success": result.success,
            "method": result.method,
            "lookup_time": result.lookup_time,
            "registration_status": result.registration_status,
            "error": result.error
        }
        
        if result.data:
            result_data["data"] = {
                "domain": result.data.domain,
                "registrar": result.data.registrar,
                "creation_date": result.data.creation_date.isoformat() if result.data.creation_date else None,
                "expiration_date": result.data.expiration_date.isoformat() if result.data.expiration_date else None,
                "updated_date": result.data.updated_date.isoformat() if result.data.updated_date else None,
                "status": result.data.status,
                "name_servers": result.data.name_servers,
                "source": result.data.source
            }
        
        data["results"].append(result_data)
    
    print(json.dumps(data, indent=2))


def display_bulk_results_csv(results: BulkLookupResult):
    """Display bulk results in CSV format"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Domain", "Registration Status", "Method", "Lookup Time (s)", 
        "Registrar", "Creation Date", "Expiration Date", "Status"
    ])
    
    # Write data rows
    for result in results.results:
        writer.writerow([
            result.domain,
            result.registration_status or ("success" if result.success else "failed"),
            result.method.upper() if result.method else "N/A",
            f"{result.lookup_time:.2f}",
            result.data.registrar if result.data and result.data.registrar else "N/A",
            result.data.creation_date.strftime("%Y-%m-%d") if result.data and result.data.creation_date else "N/A",
            result.data.expiration_date.strftime("%Y-%m-%d") if result.data and result.data.expiration_date else "N/A",
            ", ".join(result.data.status) if result.data and result.data.status else "N/A"
        ])
    
    print(output.getvalue())


def format_date(date: Optional[datetime]) -> str:
    """Format datetime for display"""
    if not date:
        return "[dim]N/A[/dim]"
    return date.strftime("%Y-%m-%d %H:%M:%S")


def format_contact(contact: Optional[dict]) -> str:
    """Format contact information for display"""
    if not contact:
        return "[dim]N/A[/dim]"
    
    parts = []
    
    # Name
    if contact.get('name') or contact.get('fn'):
        parts.append(f"[bold]{contact.get('name') or contact.get('fn')}[/bold]")
    
    # Organization
    if contact.get('organization'):
        parts.append(f"[cyan]{contact['organization']}[/cyan]")
    
    # Email
    if contact.get('email'):
        parts.append(f"📧 [blue]{contact['email']}[/blue]")
    
    # Phone
    if contact.get('phone'):
        parts.append(f"📞 [green]{contact['phone']}[/green]")
    
    # Address
    if contact.get('address'):
        parts.append(f"📍 [yellow]{contact['address']}[/yellow]")
    
    return "\n".join(parts) if parts else "[dim]N/A[/dim]"


def parse_dig_records(raw_data: str, domain: str = "") -> List[Dict[str, str]]:
    """Parse dig raw output into structured records with name and target"""
    records = []
    lines = raw_data.strip().split('\n')
    current_record_type = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this is a section header
        if line.startswith("=== ") and line.endswith(" Records ==="):
            current_record_type = line.replace("=== ", "").replace(" Records ===", "")
            continue
        
        # Skip "No DNS records found" messages
        if line == "No DNS records found" or line == "No records found":
            continue
        
        # Parse the record line
        # Format varies by record type, but generally: domain TTL IN TYPE value
        # For simpler formats, it might just be the value
        parts = line.split()
        
        if len(parts) >= 4 and parts[2] == "IN":
            # Standard DNS record format: domain TTL IN TYPE value
            record_domain = parts[0].rstrip('.')
            ttl = parts[1]
            record_type = parts[3]
            value = ' '.join(parts[4:]) if len(parts) > 4 else ""
            
            records.append({
                "type": record_type,
                "name": record_domain,
                "target": value,
                "ttl": ttl
            })
        elif current_record_type and len(parts) >= 1:
            # Simpler format - just the value, use current record type and domain
            records.append({
                "type": current_record_type,
                "name": domain,  # Use the queried domain as the name
                "target": line,
                "ttl": "N/A"  # TTL not available in this format
            })
        elif len(parts) >= 1:
            # Fallback - treat as a simple value
            records.append({
                "type": "UNKNOWN",
                "name": domain,
                "target": line,
                "ttl": "N/A"
            })
    
    return records


def display_domain_info(result: LookupResult, show_raw: bool = False):
    """Display detailed domain information"""
    if not result.success or not result.data:
        console.print(f"[red]❌ Failed to lookup {result.domain}[/red]")
        if result.error:
            console.print(f"[dim]Error: {result.error}[/dim]")
        return
    
    domain_info = result.data
    is_dig = result.method.lower() == 'dig'
    
    # Create main info panel - simplified for DIG lookups
    if is_dig:
        info_text = f"""
[bold blue]Domain:[/bold blue] {domain_info.domain}
[bold blue]Method:[/bold blue] {result.method.upper()}
[bold blue]Lookup Time:[/bold blue] {result.lookup_time:.2f}s
"""
    else:
        info_text = f"""
[bold blue]Domain:[/bold blue] {domain_info.domain}
[bold blue]Method:[/bold blue] {result.method.upper()}
[bold blue]Lookup Time:[/bold blue] {result.lookup_time:.2f}s
[bold blue]Registrar:[/bold blue] {domain_info.registrar or '[dim]N/A[/dim]'}
[bold blue]Status:[/bold blue] {', '.join(domain_info.status) if domain_info.status else '[dim]N/A[/dim]'}
"""
    
    console.print(Panel(info_text, title="[bold green]Domain Information[/bold green]", border_style="green"))
    
    # For DIG lookups, show authoritative name servers if available
    if is_dig and domain_info.name_servers:
        ns_text = "\n".join([f"[cyan]•[/cyan] [yellow]{ns}[/yellow]" for ns in domain_info.name_servers])
        console.print(Panel(
            ns_text,
            title="[bold blue]Authoritative Name Servers[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        ))
    
    # Skip dates, contacts for DIG lookups - only show for WHOIS/RDAP
    if not is_dig:
        # Create dates table
        dates_table = Table(title="[bold]Important Dates[/bold]", box=box.ROUNDED)
        dates_table.add_column("Event", style="cyan")
        dates_table.add_column("Date", style="yellow")
        
        dates_table.add_row("Creation", format_date(domain_info.creation_date))
        dates_table.add_row("Expiration", format_date(domain_info.expiration_date))
        dates_table.add_row("Last Updated", format_date(domain_info.updated_date))
        
        console.print(dates_table)
    
    # For DIG lookups, show resolved addresses/records in a dedicated table
    if is_dig and domain_info.raw_data:
        # Parse the raw data to extract structured records
        parsed_records = parse_dig_records(domain_info.raw_data, domain_info.domain)
        
        if parsed_records:
            # Create a table for resolved records
            records_table = Table(title="[bold green]Resolved Records[/bold green]", box=box.ROUNDED)
            records_table.add_column("Type", style="cyan", width=8)
            records_table.add_column("Name", style="yellow", width=25)
            records_table.add_column("Target", style="green", width=40)
            records_table.add_column("TTL", style="blue", width=8)
            
            for record in parsed_records:
                name = record["name"] if record["name"] else "[dim]N/A[/dim]"
                ttl = record["ttl"] if record["ttl"] else "[dim]N/A[/dim]"
                records_table.add_row(
                    record["type"],
                    name,
                    record["target"],
                    ttl
                )
            
            console.print(records_table)
        else:
            # Fallback to simple display if parsing fails
            records = [line.strip() for line in domain_info.raw_data.strip().split('\n') if line.strip()]
            if records:
                records_text = "\n".join([f"[cyan]•[/cyan] [yellow]{record}[/yellow]" for record in records])
                console.print(Panel(
                    records_text,
                    title="[bold green]Resolved Records[/bold green]",
                    border_style="green",
                    padding=(1, 2)
                ))
    
    # Create name servers table (show for non-DIG methods if available)
    if not is_dig and domain_info.name_servers:
        ns_table = Table(title="[bold]Name Servers[/bold]", box=box.ROUNDED)
        ns_table.add_column("Server", style="cyan")
        
        for ns in domain_info.name_servers:
            ns_table.add_row(ns)
        
        console.print(ns_table)
    
    
    # Skip contacts table for DIG lookups
    if not is_dig:
        # Create contacts table
        contacts_table = Table(title="[bold]Contact Information[/bold]", box=box.ROUNDED, show_lines=True)
        contacts_table.add_column("Type", style="cyan", vertical="top")
        contacts_table.add_column("Details", style="yellow", vertical="top")
        
        # Check if we have any contact information
        has_contacts = (
            domain_info.registrant or 
            domain_info.admin_contact or 
            domain_info.tech_contact
        )
        
        if has_contacts:
            if domain_info.registrant:
                contacts_table.add_row("Registrant", format_contact(domain_info.registrant))
            if domain_info.admin_contact:
                contacts_table.add_row("Admin", format_contact(domain_info.admin_contact))
            if domain_info.tech_contact:
                contacts_table.add_row("Technical", format_contact(domain_info.tech_contact))
        else:
            contacts_table.add_row("Registrant", "[dim]N/A[/dim]")
            contacts_table.add_row("Admin", "[dim]N/A[/dim]")
            contacts_table.add_row("Technical", "[dim]N/A[/dim]")
        
        console.print(contacts_table)
    
    # Show raw data if requested (skip for DIG as we already showed it nicely above)
    if show_raw and domain_info.raw_data:
        console.print("\n[bold]Raw Data:[/bold]")
        syntax = Syntax(domain_info.raw_data, "text", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Raw Data", border_style="blue"))
    elif not is_dig and domain_info.raw_data and len(domain_info.raw_data) < 1000:
        # Show raw data automatically if it's small and not explicitly requested
        console.print("\n[bold]Raw Data:[/bold]")
        syntax = Syntax(domain_info.raw_data, "text", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Raw Data", border_style="blue"))


def display_bulk_results(results: BulkLookupResult):
    """Display bulk lookup results"""
    # Count registration statuses
    registered_count = sum(1 for r in results.results if r.registration_status == "registered")
    not_registered_count = sum(1 for r in results.results if r.registration_status == "not_registered")
    possibly_registered_count = sum(1 for r in results.results if r.registration_status == "possibly_registered")
    
    # Summary panel
    summary_text = f"""
[bold blue]Total Domains:[/bold blue] {results.total_domains}
[bold green]✅ Registered:[/bold green] {registered_count}
[bold red]❌ Not Registered:[/bold red] {not_registered_count}
[bold yellow]⚠️ Possibly Registered:[/bold yellow] {possibly_registered_count}
[bold blue]Total Time:[/bold blue] {results.total_time:.2f}s
[bold blue]Average per Domain:[/bold blue] {results.average_time_per_domain:.2f}s
"""
    
    console.print(Panel(summary_text, title="[bold]Bulk Lookup Summary[/bold]", border_style="blue"))
    
    # Results table
    results_table = Table(title="[bold]Results[/bold]", box=box.ROUNDED)
    results_table.add_column("Domain", style="cyan")
    results_table.add_column("Registration Status", style="green")
    results_table.add_column("Method", style="yellow")
    results_table.add_column("Time", style="blue")
    results_table.add_column("Registrar", style="magenta")
    
    for result in results.results:
        # Determine status display based on registration status
        if result.registration_status == "registered":
            status = "✅ Registered"
        elif result.registration_status == "not_registered":
            status = "❌ Not Registered"
        elif result.registration_status == "possibly_registered":
            status = "⚠️ Possibly Registered"
        else:
            # Fallback to success/failure if no registration status
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
    
    console.print(results_table)


@app.command()
def lookup(
    domain: str = typer.Argument(..., help="Domain name to lookup"),
    method: str = typer.Option("auto", "--method", "-m", help="Lookup method: whois, rdap, dig, or auto"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout in seconds"),
    show_raw: bool = typer.Option(False, "--raw", "-r", help="Show raw data"),
    dig_record_type: str = typer.Option("ANY", "--dig-record", "-d", help="DNS record type for DIG lookups: A, AAAA, MX, NS, SOA, TXT, ANY"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, plain, or json"),
):
    """Lookup a single domain using WHOIS, RDAP, or DIG protocols
    
    Examples:
        domch lookup example.com
        domch lookup example.com --method whois --format plain
        domch lookup example.com --raw --timeout 60
        domch lookup example.com --method dig --dig-record MX
    """
    async def _lookup():
        checker = DomainChecker(timeout=timeout)
        result = await checker.lookup_domain(domain, method, dig_record_type)
        
        if output_format == "plain":
            display_domain_info_plain(result, show_raw)
        elif output_format == "json":
            display_domain_info_json(result, show_raw)
        else:  # rich
            display_domain_info(result, show_raw)
    
    asyncio.run(_lookup())


@app.command()
def bulk(
    domains: List[str] = typer.Argument(..., help="Domain names to lookup"),
    method: str = typer.Option("auto", "--method", "-m", help="Lookup method: whois, rdap, dig, or auto"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout in seconds"),
    max_concurrent: int = typer.Option(10, "--concurrent", "-c", help="Maximum concurrent lookups"),
    rate_limit: float = typer.Option(1.0, "--rate-limit", "-r", help="Rate limit (requests per second)"),
    dig_record_type: str = typer.Option("ANY", "--dig-record", "-d", help="DNS record type for DIG lookups: A, AAAA, MX, NS, SOA, TXT, ANY"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, plain, json, or csv"),
):
    """Lookup multiple domains"""
    async def _bulk():
        checker = DomainChecker(
            timeout=timeout,
            max_concurrent=max_concurrent,
            rate_limit=rate_limit
        )
        
        # Only show progress bar for rich output
        if output_format == "rich":
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Looking up domains...", total=len(domains))
                
                results = await checker.lookup_domains_bulk(domains, method, dig_record_type)
                progress.update(task, completed=len(domains))
        else:
            results = await checker.lookup_domains_bulk(domains, method, dig_record_type)
        
        if output_format == "plain":
            display_bulk_results_plain(results)
        elif output_format == "json":
            display_bulk_results_json(results)
        elif output_format == "csv":
            display_bulk_results_csv(results)
        else:  # rich
            display_bulk_results(results)
    
    asyncio.run(_bulk())


@app.command()
def file(
    file_path: str = typer.Argument(..., help="Path to file containing domains (one per line)"),
    method: str = typer.Option("auto", "--method", "-m", help="Lookup method: whois, rdap, dig, or auto"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout in seconds"),
    max_concurrent: int = typer.Option(10, "--concurrent", "-c", help="Maximum concurrent lookups"),
    rate_limit: float = typer.Option(1.0, "--rate-limit", "-r", help="Rate limit (requests per second)"),
    dig_record_type: str = typer.Option("ANY", "--dig-record", "-d", help="DNS record type for DIG lookups: A, AAAA, MX, NS, SOA, TXT, ANY"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, plain, json, or csv"),
):
    """Lookup domains from a file"""
    async def _file():
        checker = DomainChecker(
            timeout=timeout,
            max_concurrent=max_concurrent,
            rate_limit=rate_limit
        )
        
        # Only show progress bar for rich output
        if output_format == "rich":
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Reading file and looking up domains...", total=None)
                
                results = await checker.lookup_domains_from_file(file_path, method, dig_record_type)
                progress.update(task, completed=100)
        else:
            results = await checker.lookup_domains_from_file(file_path, method, dig_record_type)
        
        if output_format == "plain":
            display_bulk_results_plain(results)
        elif output_format == "json":
            display_bulk_results_json(results)
        elif output_format == "csv":
            display_bulk_results_csv(results)
        else:  # rich
            display_bulk_results(results)
    
    asyncio.run(_file())


@app.command()
def dig(
    domain: str = typer.Argument(..., help="Domain name to lookup"),
    record_type: str = typer.Option("ANY", "--record", "-r", help="DNS record type: A, AAAA, MX, NS, SOA, TXT, ANY"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout in seconds"),
    show_raw: bool = typer.Option(False, "--raw", help="Show raw data"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, plain, or json"),
):
    """Perform DIG lookup for a domain"""
    async def _dig():
        checker = DomainChecker(timeout=timeout)
        result = await checker.dig_lookup(domain, record_type)
        
        if output_format == "plain":
            display_domain_info_plain(result, show_raw)
        elif output_format == "json":
            display_domain_info_json(result, show_raw)
        else:  # rich
            display_domain_info(result, show_raw)
    
    asyncio.run(_dig())


@app.command()
def reverse(
    ip: str = typer.Argument(..., help="IP address to lookup"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout in seconds"),
    show_raw: bool = typer.Option(False, "--raw", help="Show raw data"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, plain, or json"),
):
    """Perform reverse DNS lookup for an IP address"""
    async def _reverse():
        checker = DomainChecker(timeout=timeout)
        result = await checker.reverse_lookup(ip)
        
        if output_format == "plain":
            display_domain_info_plain(result, show_raw)
        elif output_format == "json":
            display_domain_info_json(result, show_raw)
        else:  # rich
            display_domain_info(result, show_raw)
    
    asyncio.run(_reverse())


def display_propagation_plain(summary):
    """Display DNS propagation results in plain text format"""
    from collections import defaultdict
    
    print("DNS Propagation Check")
    print("Domain: " + summary.domain)
    print("Record Type: " + summary.record_type)
    print("Total Resolvers: " + str(summary.total_resolvers))
    print("Successful: " + str(summary.successful))
    print("Failed: " + str(summary.failed))
    print("Unique IPs: " + str(len(summary.unique_ips)))
    print("Fully Propagated: " + ("Yes" if summary.fully_propagated else "No"))
    print("Propagation: " + f"{summary.propagation_percentage:.1f}%")
    print("Total Time: " + f"{summary.total_time:.2f}s")
    
    if summary.unique_ips:
        print("Resolved IP Addresses:")
        for ip in sorted(summary.unique_ips):
            print("  " + ip)
    
    # Group results by location
    by_location = defaultdict(list)
    for result in summary.results:
        by_location[result.location].append(result)
    
    # Display results by location
    for location in sorted(by_location.keys()):
        results = by_location[location]
        print("")
        print(location + ":")
        print("Resolver\tIP\tResult\tTime")
        
        for result in results:
            if result.success:
                ips_str = ", ".join(result.resolved_ips) if result.resolved_ips else "No records"
                status = "Success"
            else:
                ips_str = result.error
                status = "Failed"
            
            print(result.resolver_name + "\t" + result.resolver_ip + "\t" + status + ": " + ips_str + "\t" + f"{result.lookup_time:.2f}s")


def display_propagation_json(summary):
    """Display DNS propagation results in JSON format"""
    from collections import defaultdict
    
    # Group results by location
    by_location = defaultdict(list)
    for result in summary.results:
        by_location[result.location].append({
            "resolver_name": result.resolver_name,
            "resolver_ip": result.resolver_ip,
            "success": result.success,
            "resolved_ips": result.resolved_ips,
            "error": result.error,
            "lookup_time": result.lookup_time
        })
    
    data = {
        "domain": summary.domain,
        "record_type": summary.record_type,
        "total_resolvers": summary.total_resolvers,
        "successful": summary.successful,
        "failed": summary.failed,
        "unique_ips": list(summary.unique_ips),
        "fully_propagated": summary.fully_propagated,
        "propagation_percentage": summary.propagation_percentage,
        "total_time": summary.total_time,
        "results_by_location": dict(by_location)
    }
    
    print(json.dumps(data, indent=2))


@app.command()
def prop(
    domain: str = typer.Argument(..., help="Domain name to check"),
    record_type: str = typer.Option("A", "--record", "-r", help="DNS record type: A, AAAA, MX, NS"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Timeout in seconds"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, plain, or json"),
):
    """Check DNS propagation across regional ISPs"""
    async def _propagation():
        checker = DomainChecker(timeout=timeout)
        
        # Only show progress bar and headers for rich output
        if output_format == "rich":
            console.print(f"\n[bold cyan]🌍 Checking DNS Propagation for {domain}[/bold cyan]")
            console.print(f"[dim]Record Type: {record_type}[/dim]\n")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Querying DNS resolvers...", total=None)
                summary = await checker.check_propagation(domain, record_type)
                progress.update(task, completed=100)
        else:
            summary = await checker.check_propagation(domain, record_type)
        
        # Display based on format
        if output_format == "plain":
            display_propagation_plain(summary)
        elif output_format == "json":
            display_propagation_json(summary)
        else:  # rich
            # Display summary
            console.print(Panel(
                f"[bold]Domain:[/bold] {summary.domain}\n"
                f"[bold]Record Type:[/bold] {summary.record_type}\n"
                f"[bold]Total Resolvers:[/bold] {summary.total_resolvers}\n"
                f"[bold]Successful:[/bold] {summary.successful}\n"
                f"[bold]Failed:[/bold] {summary.failed}\n"
                f"[bold]Unique IPs:[/bold] {len(summary.unique_ips)}\n"
                f"[bold]Fully Propagated:[/bold] {'✅ Yes' if summary.fully_propagated else '❌ No'}\n"
                f"[bold]Propagation:[/bold] {summary.propagation_percentage:.1f}%\n"
                f"[bold]Total Time:[/bold] {summary.total_time:.2f}s",
                title="Propagation Summary",
                border_style="cyan"
            ))
            
            # Display unique IPs
            if summary.unique_ips:
                console.print("\n[bold]Resolved IP Addresses:[/bold]")
                for ip in sorted(summary.unique_ips):
                    console.print(f"  • {ip}")
            
            # Group results by location
            from collections import defaultdict
            by_location = defaultdict(list)
            for result in summary.results:
                by_location[result.location].append(result)
            
            # Display results by location
            for location in sorted(by_location.keys()):
                results = by_location[location]
                console.print(f"\n[bold cyan]{location}:[/bold cyan]")
                
                table = Table(show_header=True, header_style="bold", box=box.SIMPLE)
                table.add_column("Resolver", style="dim")
                table.add_column("IP", style="dim")
                table.add_column("Result", justify="left")
                table.add_column("Time", justify="right")
                
                for result in results:
                    if result.success:
                        ips_str = ", ".join(result.resolved_ips) if result.resolved_ips else "[yellow]No records[/yellow]"
                        status = "✅"
                    else:
                        ips_str = f"[red]{result.error}[/red]"
                        status = "❌"
                    
                    table.add_row(
                        result.resolver_name,
                        result.resolver_ip,
                        f"{status} {ips_str}",
                        f"{result.lookup_time:.2f}s"
                    )
                
                console.print(table)
    
    asyncio.run(_propagation())


def display_dns_comparison_rich(domain: str, record_types: list, all_results: dict, compare_ns: str):
    """Display DNS comparison results in rich format"""
    console.print(f"\n[bold green]DNS Comparison Results[/bold green]")
    console.print("=" * 60)
    
    # Summary table
    summary_table = Table(title="Comparison Summary", box=box.ROUNDED, show_lines=True)
    summary_table.add_column("Record Type", style="cyan", width=8)
    summary_table.add_column("Default Resolvers", style="green", width=15)
    summary_table.add_column("Nameserver", style="blue", width=15)
    summary_table.add_column("Status", style="yellow", width=12)
    
    for rt in record_types:
        results = all_results[rt]
        resolver_result = results['resolver']
        ns_result = results['nameserver']
        
        # Count records
        resolver_count = 0
        ns_count = 0
        
        if resolver_result.success and resolver_result.data and resolver_result.data.raw_data:
            resolver_records = [line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()]
            # Filter out "No DNS records found" messages
            resolver_records = [r for r in resolver_records if r != "No DNS records found"]
            resolver_count = len(resolver_records)
        
        if ns_result.success and ns_result.data and ns_result.data.raw_data:
            ns_records = [line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()]
            # Filter out "No DNS records found" messages
            ns_records = [r for r in ns_records if r != "No records found"]
            ns_count = len(ns_records)
        
        # Determine status
        if resolver_result.success and ns_result.success:
            if resolver_count == 0 and ns_count == 0:
                # Both have no records - this is a match
                status = "[green]✅ Match[/green]"
            elif resolver_count == ns_count:
                # Same number of records, check if they match
                resolver_set = set([line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()])
                ns_set = set([line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()])
                # Filter out "No DNS records found" messages
                resolver_set = {r for r in resolver_set if r != "No DNS records found"}
                ns_set = {r for r in ns_set if r != "No records found"}
                if resolver_set == ns_set:
                    status = "[green]✅ Match[/green]"
                else:
                    status = "[red]❌ Different[/red]"
            else:
                status = "[red]❌ Different[/red]"
        elif not resolver_result.success and not ns_result.success:
            status = "[red]❌ Both failed[/red]"
        elif not resolver_result.success:
            status = "[red]❌ Resolver failed[/red]"
        else:
            status = "[red]❌ NS failed[/red]"
        
        summary_table.add_row(
            rt,
            f"{resolver_count} records",
            f"{ns_count} records",
            status
        )
    
    console.print(summary_table)
    
    # Detailed results for each record type
    for rt in record_types:
        results = all_results[rt]
        resolver_result = results['resolver']
        ns_result = results['nameserver']
        
        console.print(f"\n[bold cyan]{rt} Records Comparison:[/bold cyan]")
        console.print("-" * 40)
        
        # Resolver results
        console.print(f"\n[bold]Default Resolvers:[/bold]")
        if resolver_result.success and resolver_result.data:
            if resolver_result.data.raw_data:
                records = [line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()]
                for record in records:
                    console.print(f"  [green]{record}[/green]")
            else:
                console.print("  [yellow]No records found[/yellow]")
            console.print(f"  [dim]Time: {resolver_result.lookup_time:.2f}s[/dim]")
        else:
            console.print(f"  [red]Failed: {resolver_result.error}[/red]")
        
        # Nameserver results
        console.print(f"\n[bold]{compare_ns}:[/bold]")
        if ns_result.success and ns_result.data:
            if ns_result.data.raw_data:
                records = [line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()]
                for record in records:
                    console.print(f"  [green]{record}[/green]")
            else:
                console.print("  [yellow]No records found[/yellow]")
            console.print(f"  [dim]Time: {ns_result.lookup_time:.2f}s[/dim]")
        else:
            console.print(f"  [red]Failed: {ns_result.error}[/red]")
        
        # Comparison analysis for this record type
        if resolver_result.success and ns_result.success:
            resolver_records = []
            ns_records = []
            
            if resolver_result.data and resolver_result.data.raw_data:
                resolver_records = [line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()]
                # Filter out "No DNS records found" messages
                resolver_records = [r for r in resolver_records if r != "No DNS records found"]
            if ns_result.data and ns_result.data.raw_data:
                ns_records = [line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()]
                # Filter out "No DNS records found" messages
                ns_records = [r for r in ns_records if r != "No records found"]
            
            # Compare records - only show differences if there are actual differences
            resolver_set = set(resolver_records)
            ns_set = set(ns_records)
            
            # Check if both have no records (empty results)
            resolver_has_data = resolver_result.data and resolver_result.data.raw_data
            ns_has_data = ns_result.data and ns_result.data.raw_data
            
            if not resolver_has_data and not ns_has_data:
                # Both have no records - this is a match, don't show differences
                pass
            elif resolver_set != ns_set:
                console.print(f"\n[bold yellow]Differences in {rt} records:[/bold yellow]")
                
                # Show differences
                only_in_resolver = resolver_set - ns_set
                only_in_ns = ns_set - resolver_set
                
                if only_in_resolver:
                    console.print(f"  [yellow]Only in default resolvers:[/yellow]")
                    for record in sorted(only_in_resolver):
                        console.print(f"    [red]- {record}[/red]")
                
                if only_in_ns:
                    console.print(f"  [yellow]Only in {compare_ns}:[/yellow]")
                    for record in sorted(only_in_ns):
                        console.print(f"    [green]+ {record}[/green]")
    
    # Overall diagnosis
    console.print(f"\n[bold yellow]Overall Analysis:[/bold yellow]")
    
    total_matches = 0
    total_differences = 0
    total_failures = 0
    
    for rt in record_types:
        results = all_results[rt]
        resolver_result = results['resolver']
        ns_result = results['nameserver']
        
        if resolver_result.success and ns_result.success:
            # Check if both have no records (empty results)
            resolver_has_data = resolver_result.data and resolver_result.data.raw_data
            ns_has_data = ns_result.data and ns_result.data.raw_data
            
            if not resolver_has_data and not ns_has_data:
                # Both have no records - this is a match
                total_matches += 1
            elif resolver_has_data and ns_has_data:
                # Both have data, compare the actual records
                resolver_set = set([line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()])
                ns_set = set([line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()])
                # Filter out "No DNS records found" messages
                resolver_set = {r for r in resolver_set if r != "No DNS records found"}
                ns_set = {r for r in ns_set if r != "No records found"}
                if resolver_set == ns_set:
                    total_matches += 1
                else:
                    total_differences += 1
            else:
                # One has data, one doesn't - this is a difference
                total_differences += 1
        else:
            total_failures += 1
    
    if total_differences == 0 and total_failures == 0:
        console.print("  [green]✅ All record types match perfectly![/green]")
        console.print("  [dim]Both resolvers returned identical DNS records for all types.[/dim]")
    elif total_differences > 0:
        console.print(f"  [red]❌ Found differences in {total_differences} record type(s)[/red]")
        console.print("  [dim]Possible issues: DNS propagation, caching, or configuration differences[/dim]")
    else:
        console.print(f"  [yellow]⚠️  {total_failures} record type(s) failed to query[/yellow]")
        console.print("  [dim]Check network connectivity and nameserver availability[/dim]")


def display_dns_comparison_plain(domain: str, record_types: list, all_results: dict, compare_ns: str):
    """Display DNS comparison results in plain format"""
    print("DNS Comparison Results")
    print("=" * 40)
    
    # Summary
    print("\nComparison Summary:")
    print("-" * 20)
    for rt in record_types:
        results = all_results[rt]
        resolver_result = results['resolver']
        ns_result = results['nameserver']
        
        # Count records
        resolver_count = 0
        ns_count = 0
        
        if resolver_result.success and resolver_result.data and resolver_result.data.raw_data:
            resolver_records = [line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()]
            # Filter out "No DNS records found" messages
            resolver_records = [r for r in resolver_records if r != "No DNS records found"]
            resolver_count = len(resolver_records)
        
        if ns_result.success and ns_result.data and ns_result.data.raw_data:
            ns_records = [line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()]
            # Filter out "No DNS records found" messages
            ns_records = [r for r in ns_records if r != "No records found"]
            ns_count = len(ns_records)
        
        # Determine status
        if resolver_result.success and ns_result.success:
            if resolver_count == 0 and ns_count == 0:
                # Both have no records - this is a match
                status = "✅ Match"
            elif resolver_count == ns_count:
                # Same number of records, check if they match
                resolver_set = set([line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()])
                ns_set = set([line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()])
                # Filter out "No DNS records found" messages
                resolver_set = {r for r in resolver_set if r != "No DNS records found"}
                ns_set = {r for r in ns_set if r != "No records found"}
                if resolver_set == ns_set:
                    status = "✅ Match"
                else:
                    status = "❌ Different"
            else:
                status = "❌ Different"
        elif not resolver_result.success and not ns_result.success:
            status = "❌ Both failed"
        elif not resolver_result.success:
            status = "❌ Resolver failed"
        else:
            status = "❌ NS failed"
        
        print(f"{rt:8} | Default: {resolver_count:2} records | {compare_ns}: {ns_count:2} records | {status}")
    
    # Detailed results for each record type
    for rt in record_types:
        results = all_results[rt]
        resolver_result = results['resolver']
        ns_result = results['nameserver']
        
        print(f"\n{rt} Records Comparison:")
        print("-" * 30)
        
        # Resolver results
        print("\nDefault Resolvers:")
        if resolver_result.success and resolver_result.data:
            if resolver_result.data.raw_data:
                records = [line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()]
                for record in records:
                    print("  " + record)
            else:
                print("  No records found")
            print("  Time: " + f"{resolver_result.lookup_time:.2f}s")
        else:
            print("  Failed: " + resolver_result.error)
        
        # Nameserver results
        print(f"\n{compare_ns}:")
        if ns_result.success and ns_result.data:
            if ns_result.data.raw_data:
                records = [line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()]
                for record in records:
                    print("  " + record)
            else:
                print("  No records found")
            print("  Time: " + f"{ns_result.lookup_time:.2f}s")
        else:
            print("  Failed: " + ns_result.error)
        
        # Comparison analysis for this record type
        if resolver_result.success and ns_result.success:
            resolver_records = []
            ns_records = []
            
            if resolver_result.data and resolver_result.data.raw_data:
                resolver_records = [line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()]
                # Filter out "No DNS records found" messages
                resolver_records = [r for r in resolver_records if r != "No DNS records found"]
            if ns_result.data and ns_result.data.raw_data:
                ns_records = [line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()]
                # Filter out "No DNS records found" messages
                ns_records = [r for r in ns_records if r != "No records found"]
            
            # Compare records - only show differences if there are actual differences
            resolver_set = set(resolver_records)
            ns_set = set(ns_records)
            
            # Check if both have no records (empty results)
            resolver_has_data = resolver_result.data and resolver_result.data.raw_data
            ns_has_data = ns_result.data and ns_result.data.raw_data
            
            if not resolver_has_data and not ns_has_data:
                # Both have no records - this is a match, don't show differences
                pass
            elif resolver_set != ns_set:
                print(f"\nDifferences in {rt} records:")
                
                # Show differences
                only_in_resolver = resolver_set - ns_set
                only_in_ns = ns_set - resolver_set
                
                if only_in_resolver:
                    print(f"  Only in default resolvers:")
                    for record in sorted(only_in_resolver):
                        print("    - " + record)
                
                if only_in_ns:
                    print(f"  Only in {compare_ns}:")
                    for record in sorted(only_in_ns):
                        print("    + " + record)
    
    # Overall diagnosis
    print(f"\nOverall Analysis:")
    
    total_matches = 0
    total_differences = 0
    total_failures = 0
    
    for rt in record_types:
        results = all_results[rt]
        resolver_result = results['resolver']
        ns_result = results['nameserver']
        
        if resolver_result.success and ns_result.success:
            # Check if both have no records (empty results)
            resolver_has_data = resolver_result.data and resolver_result.data.raw_data
            ns_has_data = ns_result.data and ns_result.data.raw_data
            
            if not resolver_has_data and not ns_has_data:
                # Both have no records - this is a match
                total_matches += 1
            elif resolver_has_data and ns_has_data:
                # Both have data, compare the actual records
                resolver_set = set([line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()])
                ns_set = set([line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()])
                # Filter out "No DNS records found" messages
                resolver_set = {r for r in resolver_set if r != "No DNS records found"}
                ns_set = {r for r in ns_set if r != "No records found"}
                if resolver_set == ns_set:
                    total_matches += 1
                else:
                    total_differences += 1
            else:
                # One has data, one doesn't - this is a difference
                total_differences += 1
        else:
            total_failures += 1
    
    if total_differences == 0 and total_failures == 0:
        print("  ✅ All record types match perfectly!")
        print("  Both resolvers returned identical DNS records for all types.")
    elif total_differences > 0:
        print(f"  ❌ Found differences in {total_differences} record type(s)")
        print("  Possible issues: DNS propagation, caching, or configuration differences")
    else:
        print(f"  ⚠️  {total_failures} record type(s) failed to query")
        print("  Check network connectivity and nameserver availability")


def display_dns_comparison_json(domain: str, record_types: list, all_results: dict, compare_ns: str):
    """Display DNS comparison results in JSON format"""
    import json
    
    data = {
        "domain": domain,
        "record_types": record_types,
        "compare_nameserver": compare_ns,
        "results": {}
    }
    
    # Process each record type
    for rt in record_types:
        results = all_results[rt]
        resolver_result = results['resolver']
        ns_result = results['nameserver']
        
        resolver_records = []
        ns_records = []
        
        if resolver_result.success and resolver_result.data and resolver_result.data.raw_data:
            resolver_records = [line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()]
        if ns_result.success and ns_result.data and ns_result.data.raw_data:
            ns_records = [line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()]
        
        resolver_set = set(resolver_records)
        ns_set = set(ns_records)
        
        data["results"][rt] = {
            "resolver_results": {
                "success": resolver_result.success,
                "records": resolver_records,
                "time": resolver_result.lookup_time,
                "error": resolver_result.error if not resolver_result.success else None
            },
            "nameserver_results": {
                "success": ns_result.success,
                "records": ns_records,
                "time": ns_result.lookup_time,
                "error": ns_result.error if not ns_result.success else None
            },
            "comparison": {
                "match": resolver_set == ns_set,
                "only_in_resolver": list(resolver_set - ns_set),
                "only_in_nameserver": list(ns_set - resolver_set),
                "common_records": list(resolver_set & ns_set)
            }
        }
    
    # Overall summary
    total_matches = 0
    total_differences = 0
    total_failures = 0
    
    for rt in record_types:
        results = all_results[rt]
        resolver_result = results['resolver']
        ns_result = results['nameserver']
        
        if resolver_result.success and ns_result.success:
            # Check if both have no records (empty results)
            resolver_has_data = resolver_result.data and resolver_result.data.raw_data
            ns_has_data = ns_result.data and ns_result.data.raw_data
            
            if not resolver_has_data and not ns_has_data:
                # Both have no records - this is a match
                total_matches += 1
            elif resolver_has_data and ns_has_data:
                # Both have data, compare the actual records
                resolver_set = set([line.strip() for line in resolver_result.data.raw_data.strip().split('\n') if line.strip()])
                ns_set = set([line.strip() for line in ns_result.data.raw_data.strip().split('\n') if line.strip()])
                # Filter out "No DNS records found" messages
                resolver_set = {r for r in resolver_set if r != "No DNS records found"}
                ns_set = {r for r in ns_set if r != "No records found"}
                if resolver_set == ns_set:
                    total_matches += 1
                else:
                    total_differences += 1
            else:
                # One has data, one doesn't - this is a difference
                total_differences += 1
        else:
            total_failures += 1
    
    data["summary"] = {
        "total_record_types": len(record_types),
        "matches": total_matches,
        "differences": total_differences,
        "failures": total_failures,
        "overall_status": "perfect_match" if total_differences == 0 and total_failures == 0 else "differences_found" if total_differences > 0 else "failures"
    }
    
    print(json.dumps(data, indent=2))


@app.command()
def compare(
    domain: str = typer.Argument(..., help="Domain name to compare DNS results for"),
    record_type: str = typer.Option("ALL", "--record", "-r", help="DNS record type to compare: A, AAAA, CNAME, MX, TXT, ALL (default: ALL)"),
    custom_ns: str = typer.Option(None, "--nameserver", "-n", help="Custom nameserver to compare against (e.g., 8.8.8.8 or ns1.example.com)"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Timeout in seconds (default: 10)"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, plain, json (default: rich)"),
):
    """Compare DNS results between resolver NS and specified NS set to diagnose DNS issues
    
    This command performs DNS lookups using both the system's default resolvers
    and a specified nameserver, then compares the results to help diagnose
    DNS configuration issues, propagation problems, or inconsistencies.
    
    By default, compares ALL record types (A, AAAA, MX, TXT) excluding NS and SOA.
    Use --record to compare a specific record type only.
    
    Examples:
        domch compare example.com                    # Compare all record types
        domch compare example.com --record MX        # Compare only MX records
        domch compare example.com --nameserver 8.8.8.8
        domch compare example.com --format plain
    """
    async def _compare():
        checker = DomainChecker(timeout=timeout)
        
        # Get domain's authoritative nameservers first
        console.print(f"[bold blue]DNS Comparison for: {domain}[/bold blue]")
        
        # Determine record types to compare
        if record_type.upper() == "ALL":
            record_types = ["A", "AAAA", "CNAME", "MX", "TXT"]  # Exclude NS and SOA as requested
            console.print(f"[cyan]Record Types:[/cyan] {', '.join(record_types)} (excluding NS and SOA)")
        else:
            record_types = [record_type.upper()]
            console.print(f"[cyan]Record Type:[/cyan] {record_type}")
        
        # Get authoritative nameservers
        ns_result = await checker.lookup_domain(domain, "dig", "NS")
        authoritative_ns = []
        if ns_result.success and ns_result.data and ns_result.data.name_servers:
            authoritative_ns = ns_result.data.name_servers
            console.print(f"[cyan]Authoritative NS:[/cyan] {', '.join(authoritative_ns)}")
        
        # Determine nameserver to compare against
        if custom_ns:
            compare_ns = custom_ns
            console.print(f"[cyan]Comparing against:[/cyan] {compare_ns}")
        elif authoritative_ns:
            compare_ns = authoritative_ns[0]  # Use first authoritative NS
            console.print(f"[cyan]Comparing against:[/cyan] {compare_ns} (first authoritative NS)")
        else:
            console.print("[red]❌ Could not determine nameserver to compare against[/red]")
            return
        
        console.print("")
        
        # Perform lookups for all record types
        all_results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            for rt in record_types:
                task1 = progress.add_task(f"Querying default resolvers for {rt}...", total=None)
                resolver_result = await checker.lookup_domain(domain, "dig", rt)
                progress.update(task1, description=f"Default resolvers queried for {rt}")
                
                task2 = progress.add_task(f"Querying {compare_ns} for {rt}...", total=None)
                ns_result = await checker.lookup_domain_with_ns(domain, rt, compare_ns)
                progress.update(task2, description=f"{compare_ns} queried for {rt}")
                
                all_results[rt] = {
                    'resolver': resolver_result,
                    'nameserver': ns_result
                }
        
        # Compare results
        if output_format == "plain":
            display_dns_comparison_plain(domain, record_types, all_results, compare_ns)
        elif output_format == "json":
            display_dns_comparison_json(domain, record_types, all_results, compare_ns)
        else:
            display_dns_comparison_rich(domain, record_types, all_results, compare_ns)
    
    asyncio.run(_compare())


@app.command()
def interactive():
    """Start interactive mode"""
    console.print("[bold green]Domain Checker Interactive Mode[/bold green]")
    console.print("Type 'help' for commands, 'quit' to exit\n")
    
    checker = DomainChecker()
    
    while True:
        try:
            command = typer.prompt("domch> ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                break
            elif command.lower() == 'help':
                console.print("""
[bold]Available commands:[/bold]
  lookup <domain> [method] - Lookup a single domain
  bulk <domain1> <domain2> ... - Lookup multiple domains
  dig <domain> [record_type] - DIG lookup for a domain
  reverse <ip> - Reverse DNS lookup for an IP
  compare <domain> - Compare WHOIS and RDAP for a domain
  help - Show this help
  quit - Exit interactive mode
""")
            elif command.startswith('lookup '):
                parts = command.split()
                if len(parts) >= 2:
                    domain = parts[1]
                    method = parts[2] if len(parts) > 2 else "auto"
                    
                    async def _interactive_lookup():
                        result = await checker.lookup_domain(domain, method)
                        display_domain_info(result)
                    
                    asyncio.run(_interactive_lookup())
                else:
                    console.print("[red]Usage: lookup <domain> [method][/red]")
            elif command.startswith('bulk '):
                parts = command.split()
                if len(parts) >= 2:
                    domains = parts[1:]
                    
                    async def _interactive_bulk():
                        results = await checker.lookup_domains_bulk(domains)
                        display_bulk_results(results)
                    
                    asyncio.run(_interactive_bulk())
                else:
                    console.print("[red]Usage: bulk <domain1> <domain2> ...[/red]")
            elif command.startswith('compare '):
                parts = command.split()
                if len(parts) >= 2:
                    domain = parts[1]
                    
                    async def _interactive_compare():
                        comparison = await checker.compare_methods(domain)
                        
                        console.print(f"[bold blue]Comparing methods for: {domain}[/bold blue]\n")
                        
                        console.print("[bold]WHOIS Results:[/bold]")
                        display_domain_info(comparison["whois"])
                        
                        console.print("\n[bold]RDAP Results:[/bold]")
                        display_domain_info(comparison["rdap"])
                    
                    asyncio.run(_interactive_compare())
                else:
                    console.print("[red]Usage: compare <domain>[/red]")
            elif command.startswith('dig '):
                parts = command.split()
                if len(parts) >= 2:
                    domain = parts[1]
                    record_type = parts[2] if len(parts) > 2 else "ANY"
                    
                    async def _interactive_dig():
                        result = await checker.dig_lookup(domain, record_type)
                        display_domain_info(result)
                    
                    asyncio.run(_interactive_dig())
                else:
                    console.print("[red]Usage: dig <domain> [record_type][/red]")
            elif command.startswith('reverse '):
                parts = command.split()
                if len(parts) >= 2:
                    ip = parts[1]
                    
                    async def _interactive_reverse():
                        result = await checker.reverse_lookup(ip)
                        display_domain_info(result)
                    
                    asyncio.run(_interactive_reverse())
                else:
                    console.print("[red]Usage: reverse <ip>[/red]")
            elif command:
                console.print(f"[red]Unknown command: {command}[/red]")
                console.print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            console.print("\n[bold]Goodbye![/bold]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def update(
    force: bool = typer.Option(False, "--force", "-f", help="Force update even if no changes detected"),
    check_only: bool = typer.Option(False, "--check", "-c", help="Only check for updates, don't install"),
    rollback: Optional[str] = typer.Option(None, "--rollback", "-r", help="Rollback to specified version"),
    no_auto_reinstall: bool = typer.Option(False, "--no-auto-reinstall", help="Don't automatically reinstall package after update")
):
    """Update domain checker from repository"""
    async def _update():
        updater = DomainCheckerUpdater()
        
        if rollback:
            updater.rollback(rollback)
            return
        
        if check_only:
            has_updates, latest_version, update_info = await updater.check_for_updates()
            
            if has_updates:
                console.print(f"[yellow]Update available: {latest_version}[/yellow]")
                if update_info:
                    if "release_notes" in update_info:
                        console.print(f"[dim]Release Notes: {update_info['release_notes'][:200]}...[/dim]")
                    if "commit_message" in update_info:
                        console.print(f"[dim]Latest Commit: {update_info['commit_message'][:100]}...[/dim]")
            else:
                console.print("[green]✅ You're running the latest version![/green]")
        else:
            await updater.update_installation(force=force, auto_reinstall=not no_auto_reinstall)
    
    asyncio.run(_update())


@app.command()
def help():
    """Show comprehensive help with all available flags and options"""
    from . import __version__
    
    help_text = f"""[bold blue]Domain Checker v{__version__}[/bold blue] - Comprehensive Help

[bold green]COMMANDS:[/bold green]

[bold cyan]lookup[/bold cyan] [yellow]<domain>[/yellow]
  Lookup a single domain
  [dim]Flags:[/dim]
    [cyan]-m, --method[/cyan] [yellow]<method>[/yellow]     Lookup method: whois, rdap, dig, auto (default: auto)
    [cyan]-t, --timeout[/cyan] [yellow]<seconds>[/yellow]   Timeout in seconds (default: 30)
    [cyan]-r, --raw[/cyan]                Show raw data
    [cyan]-d, --dig-record[/cyan] [yellow]<type>[/yellow]   DNS record type for DIG: A, AAAA, MX, NS, SOA, TXT, ANY (default: ANY)
    [cyan]-f, --format[/cyan] [yellow]<format>[/yellow]     Output format: rich, plain, json (default: rich)

[bold cyan]bulk[/bold cyan] [yellow]<domain1> <domain2> ...[/yellow]
  Check multiple domains
  [dim]Flags:[/dim]
    [cyan]-m, --method[/cyan] [yellow]<method>[/yellow]     Lookup method: whois, rdap, dig, auto (default: auto)
    [cyan]-t, --timeout[/cyan] [yellow]<seconds>[/yellow]   Timeout in seconds (default: 30)
    [cyan]-c, --concurrent[/cyan] [yellow]<number>[/yellow] Maximum concurrent lookups (default: 10)
    [cyan]-f, --format[/cyan] [yellow]<format>[/yellow]     Output format: rich, plain, json, csv (default: rich)

[bold cyan]file[/bold cyan] [yellow]<file_path>[/yellow]
  Check domains from a file (one per line)
  [dim]Flags:[/dim]
    [cyan]-m, --method[/cyan] [yellow]<method>[/yellow]     Lookup method: whois, rdap, dig, auto (default: auto)
    [cyan]-t, --timeout[/cyan] [yellow]<seconds>[/yellow]   Timeout in seconds (default: 30)
    [cyan]-c, --concurrent[/cyan] [yellow]<number>[/yellow] Maximum concurrent lookups (default: 10)
    [cyan]-f, --format[/cyan] [yellow]<format>[/yellow]     Output format: rich, plain, json, csv (default: rich)

[bold cyan]dig[/bold cyan] [yellow]<domain>[/yellow]
  Perform DNS lookup using DIG
  [dim]Flags:[/dim]
    [cyan]-r, --record[/cyan] [yellow]<type>[/yellow]       DNS record type: A, AAAA, MX, NS, SOA, TXT, ANY (default: ANY)
    [cyan]-t, --timeout[/cyan] [yellow]<seconds>[/yellow]   Timeout in seconds (default: 30)
    [cyan]-f, --format[/cyan] [yellow]<format>[/yellow]     Output format: rich, plain, json (default: rich)

[bold cyan]reverse[/bold cyan] [yellow]<ip_address>[/yellow]
  Perform reverse DNS lookup
  [dim]Flags:[/dim]
    [cyan]-t, --timeout[/cyan] [yellow]<seconds>[/yellow]   Timeout in seconds (default: 30)
    [cyan]-f, --format[/cyan] [yellow]<format>[/yellow]     Output format: rich, plain, json (default: rich)

[bold cyan]prop[/bold cyan] [yellow]<domain>[/yellow]
  Check DNS propagation across multiple resolvers
  [dim]Flags:[/dim]
    [cyan]-r, --record[/cyan] [yellow]<type>[/yellow]       DNS record type: A, AAAA, MX, NS (default: A)
    [cyan]-t, --timeout[/cyan] [yellow]<seconds>[/yellow]   Timeout in seconds (default: 10)
    [cyan]-f, --format[/cyan] [yellow]<format>[/yellow]     Output format: rich, plain, json (default: rich)

[bold cyan]compare[/bold cyan] [yellow]<domain>[/yellow]
  Compare DNS results between resolver NS and specified NS set
  [dim]Flags:[/dim]
    [cyan]-r, --record[/cyan] [yellow]<type>[/yellow]       DNS record type: A, AAAA, CNAME, MX, TXT, ALL (default: ALL)
    [cyan]-n, --nameserver[/cyan] [yellow]<ns>[/yellow]     Custom nameserver to compare against (e.g., 8.8.8.8)
    [cyan]-t, --timeout[/cyan] [yellow]<seconds>[/yellow]   Timeout in seconds (default: 10)
    [cyan]-f, --format[/cyan] [yellow]<format>[/yellow]     Output format: rich, plain, json (default: rich)

[bold cyan]interactive[/bold cyan]
  Start interactive mode

[bold cyan]update[/bold cyan]
  Update Domain Checker to latest version
  [dim]Flags:[/dim]
    [cyan]-f, --force[/cyan]               Force update even if no changes detected
    [cyan]-c, --check[/cyan]               Only check for updates, don't install
    [cyan]-r, --rollback[/cyan] [yellow]<version>[/yellow]  Rollback to specified version
    [cyan]--no-auto-reinstall[/cyan]       Don't automatically reinstall package after update

[bold cyan]about[/bold cyan]
  Show version information and credits

[bold green]OUTPUT FORMATS:[/bold green]
  [cyan]rich[/cyan]   Beautiful, colorful terminal output (default)
  [cyan]plain[/cyan]  Clean, copy/paste friendly text
  [cyan]json[/cyan]   Structured JSON output
  [cyan]csv[/cyan]    Comma-separated values (bulk commands only)

[bold green]EXAMPLES:[/bold green]
  [dim]# Basic domain lookup[/dim]
  [cyan]domch lookup example.com[/cyan]

  [dim]# Check multiple domains with plain output[/dim]
  [cyan]domch bulk example.com google.com --format plain[/cyan]

  [dim]# DNS lookup for MX records using lookup command[/dim]
  [cyan]domch lookup example.com --method dig --dig-record MX[/cyan]

  [dim]# DNS lookup for MX records using dig command[/dim]
  [cyan]domch dig example.com --record MX[/cyan]

  [dim]# Compare DNS results between resolvers and specific nameserver[/dim]
  [cyan]domch compare example.com --nameserver 8.8.8.8[/cyan]

  [dim]# Check domains from file with JSON output[/dim]
  [cyan]domch file domains.txt --format json[/cyan]

  [dim]# Force update to latest version[/dim]
  [cyan]domch update --force[/cyan]

[bold green]MORE HELP:[/bold green]
  [cyan]domch <command> --help[/cyan]  Show help for specific command
  [cyan]domch about[/cyan]             Show version and feature information"""
    
    console.print(help_text)


@app.command()
def about():
    """Show version information and credits"""
    from . import __version__
    from datetime import datetime
    
    # Get current date in MM/DD/YYYY format
    current_date = datetime.now().strftime("%m/%d/%Y")
    
    # Create a beautiful about panel
    about_text = f"""[bold blue]Domain Checker[/bold blue] v[bold green]{__version__}[/bold green]
[dim]Updated: {current_date}[/dim]

[bold]Created by:[/bold] [cyan]Zac Roach[/cyan]

[bold]Description:[/bold] Asynchronous domain checker with WHOIS, RDAP, and DIG support

[bold]Features:[/bold]
• Fast asynchronous domain lookups
• WHOIS, RDAP, and DIG protocol support
• DNS propagation checking
• Bulk domain processing
• Beautiful CLI interface
• MCP server integration

[bold]Repository:[/bold] [link=https://github.com/TheZacillac/domain-checker]https://github.com/TheZacillac/domain-checker[/link]
[bold]License:[/bold] MIT

[bold]Usage:[/bold]
• CLI: [cyan]domch lookup example.com[/cyan]

[dim]Use 'domch help' for comprehensive help with all flags[/dim]"""
    
    panel = Panel(
        about_text,
        title="[bold blue]About Domain Checker[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
