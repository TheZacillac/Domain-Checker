"""
Command-line interface for domain checker
"""

import asyncio
import typer
from typing import List, Optional
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
    add_completion=False
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


def display_domain_info_plain(result: LookupResult):
    """Display domain information in plain text format"""
    if not result.success or not result.data:
        print(f"Failed to lookup {result.domain}")
        if result.error:
            print(f"Error: {result.error}")
        return
    
    domain_info = result.data
    is_dig = result.method.lower() == 'dig'
    
    print("=" * 60)
    print("DOMAIN INFORMATION")
    print("=" * 60)
    print(f"Domain: {domain_info.domain}")
    print(f"Method: {result.method.upper()}")
    print(f"Lookup Time: {result.lookup_time:.2f}s")
    
    if not is_dig:
        print(f"Registrar: {domain_info.registrar or 'N/A'}")
        print(f"Status: {', '.join(domain_info.status) if domain_info.status else 'N/A'}")
    
    # Name servers
    if domain_info.name_servers:
        print("\nNAME SERVERS:")
        for ns in domain_info.name_servers:
            print(f"  {ns}")
    
    # For DIG lookups, show resolved records
    if is_dig and domain_info.raw_data:
        records = [line.strip() for line in domain_info.raw_data.strip().split('\n') if line.strip()]
        if records:
            print("\nRESOLVED RECORDS:")
            for record in records:
                print(f"  {record}")
    
    # Dates (skip for DIG)
    if not is_dig:
        print("\nIMPORTANT DATES:")
        print(f"  Creation: {format_date_plain(domain_info.creation_date)}")
        print(f"  Expiration: {format_date_plain(domain_info.expiration_date)}")
        print(f"  Last Updated: {format_date_plain(domain_info.updated_date)}")
    
    # Contacts (skip for DIG)
    if not is_dig:
        has_contacts = (
            domain_info.registrant or 
            domain_info.admin_contact or 
            domain_info.tech_contact
        )
        
        if has_contacts:
            print("\nCONTACT INFORMATION:")
            if domain_info.registrant:
                print(f"  Registrant: {format_contact_plain(domain_info.registrant)}")
            if domain_info.admin_contact:
                print(f"  Admin: {format_contact_plain(domain_info.admin_contact)}")
            if domain_info.tech_contact:
                print(f"  Technical: {format_contact_plain(domain_info.tech_contact)}")
    
    print("=" * 60)


def display_domain_info_json(result: LookupResult):
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
            "raw_data": result.data.raw_data
        }
    
    print(json.dumps(data, indent=2))


def display_bulk_results_plain(results: BulkLookupResult):
    """Display bulk results in plain text format"""
    registered_count = sum(1 for r in results.results if r.registration_status == "registered")
    not_registered_count = sum(1 for r in results.results if r.registration_status == "not_registered")
    possibly_registered_count = sum(1 for r in results.results if r.registration_status == "possibly_registered")
    
    print("=" * 80)
    print("BULK LOOKUP SUMMARY")
    print("=" * 80)
    print(f"Total Domains: {results.total_domains}")
    print(f"Registered: {registered_count}")
    print(f"Not Registered: {not_registered_count}")
    print(f"Possibly Registered: {possibly_registered_count}")
    print(f"Total Time: {results.total_time:.2f}s")
    print(f"Average per Domain: {results.average_time_per_domain:.2f}s")
    print("=" * 80)
    print(f"\n{'Domain':<30} {'Status':<20} {'Method':<10} {'Time':<10} {'Registrar':<30}")
    print("-" * 100)
    
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
        
        print(f"{result.domain:<30} {status:<20} {method:<10} {time_str:<10} {registrar:<30}")


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


def display_domain_info(result: LookupResult):
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
    
    # For DIG lookups, show resolved addresses/records in a dedicated box
    if is_dig and domain_info.raw_data:
        # Parse the raw data to extract resolved records
        records = [line.strip() for line in domain_info.raw_data.strip().split('\n') if line.strip()]
        
        if records:
            # Create a panel for resolved records
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
    if not is_dig and domain_info.raw_data and len(domain_info.raw_data) < 1000:
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
    """Lookup a single domain"""
    async def _lookup():
        checker = DomainChecker(timeout=timeout)
        result = await checker.lookup_domain(domain, method, dig_record_type)
        
        if output_format == "plain":
            display_domain_info_plain(result)
        elif output_format == "json":
            display_domain_info_json(result)
        else:  # rich
            display_domain_info(result)
    
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
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, plain, or json"),
):
    """Perform DIG lookup for a domain"""
    async def _dig():
        checker = DomainChecker(timeout=timeout)
        result = await checker.dig_lookup(domain, record_type)
        
        if output_format == "plain":
            display_domain_info_plain(result)
        elif output_format == "json":
            display_domain_info_json(result)
        else:  # rich
            display_domain_info(result)
    
    asyncio.run(_dig())


@app.command()
def reverse(
    ip: str = typer.Argument(..., help="IP address to lookup"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout in seconds"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, plain, or json"),
):
    """Perform reverse DNS lookup for an IP address"""
    async def _reverse():
        checker = DomainChecker(timeout=timeout)
        result = await checker.reverse_lookup(ip)
        
        if output_format == "plain":
            display_domain_info_plain(result)
        elif output_format == "json":
            display_domain_info_json(result)
        else:  # rich
            display_domain_info(result)
    
    asyncio.run(_reverse())


def display_propagation_plain(summary):
    """Display DNS propagation results in plain text format"""
    from collections import defaultdict
    
    print("=" * 80)
    print("DNS PROPAGATION CHECK")
    print("=" * 80)
    print(f"Domain: {summary.domain}")
    print(f"Record Type: {summary.record_type}")
    print(f"Total Resolvers: {summary.total_resolvers}")
    print(f"Successful: {summary.successful}")
    print(f"Failed: {summary.failed}")
    print(f"Unique IPs: {len(summary.unique_ips)}")
    print(f"Fully Propagated: {'Yes' if summary.fully_propagated else 'No'}")
    print(f"Propagation: {summary.propagation_percentage:.1f}%")
    print(f"Total Time: {summary.total_time:.2f}s")
    
    if summary.unique_ips:
        print("\nRESOLVED IP ADDRESSES:")
        for ip in sorted(summary.unique_ips):
            print(f"  {ip}")
    
    # Group results by location
    by_location = defaultdict(list)
    for result in summary.results:
        by_location[result.location].append(result)
    
    # Display results by location
    for location in sorted(by_location.keys()):
        results = by_location[location]
        print(f"\n{location}:")
        print(f"{'Resolver':<25} {'IP':<20} {'Result':<40} {'Time':<10}")
        print("-" * 100)
        
        for result in results:
            if result.success:
                ips_str = ", ".join(result.resolved_ips) if result.resolved_ips else "No records"
                status = "Success"
            else:
                ips_str = result.error
                status = "Failed"
            
            print(f"{result.resolver_name:<25} {result.resolver_ip:<20} {status}: {ips_str:<40} {result.lookup_time:.2f}s")
    
    print("=" * 80)


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


@app.command()
def compare(
    domain: str = typer.Argument(..., help="Domain name to compare"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout in seconds"),
):
    """Compare WHOIS and RDAP results for a domain"""
    async def _compare():
        checker = DomainChecker(timeout=timeout)
        comparison = await checker.compare_methods(domain)
        
        console.print(f"[bold blue]Comparing methods for: {domain}[/bold blue]\n")
        
        # WHOIS results
        console.print("[bold]WHOIS Results:[/bold]")
        display_domain_info(comparison["whois"])
        
        console.print("\n" + "="*50 + "\n")
        
        # RDAP results
        console.print("[bold]RDAP Results:[/bold]")
        display_domain_info(comparison["rdap"])
        
        # Comparison summary
        comp = comparison["comparison"]
        summary_text = f"""
[bold blue]Comparison Summary:[/bold blue]
[bold]WHOIS Success:[/bold] {'✅' if comp['whois_success'] else '❌'} ({comp['whois_time']:.2f}s)
[bold]RDAP Success:[/bold] {'✅' if comp['rdap_success'] else '❌'} ({comp['rdap_time']:.2f}s)
[bold]Data Available:[/bold] WHOIS: {'✅' if comp['data_available']['whois'] else '❌'}, RDAP: {'✅' if comp['data_available']['rdap'] else '❌'}
"""
        console.print(Panel(summary_text, title="[bold]Comparison Summary[/bold]", border_style="yellow"))
    
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
def gui():
    """Launch the user-friendly graphical interface"""
    try:
        from .gui import run_gui
        run_gui()
    except ImportError as e:
        console.print(f"[red]❌ GUI not available: {e}[/red]")
        console.print("[yellow]To install the GUI dependency, run one of these commands:[/yellow]")
        console.print("[cyan]  pip install textual[/cyan]")
        console.print("[cyan]  pipx inject domain-checker textual[/cyan]")
        console.print("[dim]Note: If you installed with pipx, use 'pipx inject' to add dependencies[/dim]")
    except Exception as e:
        console.print(f"[red]❌ Error launching GUI: {e}[/red]")


@app.command()
def about():
    """Show version information and credits"""
    from . import __version__
    
    # Create a beautiful about panel
    about_text = f"""[bold blue]Domain Checker[/bold blue] v[bold green]{__version__}[/bold green]

[bold]Created by:[/bold] [cyan]Zac Roach[/cyan]

[bold]Description:[/bold] Asynchronous domain checker with WHOIS, RDAP, and DIG support

[bold]Features:[/bold]
• Fast asynchronous domain lookups
• WHOIS, RDAP, and DIG protocol support
• DNS propagation checking
• Bulk domain processing
• Beautiful CLI interface
• User-friendly GUI interface
• MCP server integration

[bold]Repository:[/bold] [link=https://github.com/TheZacillac/domain-checker]https://github.com/TheZacillac/domain-checker[/link]
[bold]License:[/bold] MIT

[bold]Usage:[/bold]
• CLI: [cyan]domch lookup example.com[/cyan]
• GUI: [cyan]domch gui[/cyan] (user-friendly interface)

[dim]Use 'domch --help' to see available commands[/dim]"""
    
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
