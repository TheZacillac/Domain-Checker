"""
Command-line interface for domain checker
"""

import asyncio
import typer
from typing import List, Optional
from pathlib import Path
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

app = typer.Typer(
    name="domain-check",
    help="Asynchronous domain checker with WHOIS and RDAP support",
    add_completion=False
)
console = Console()


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
    
    # Create main info panel
    info_text = f"""
[bold blue]Domain:[/bold blue] {domain_info.domain}
[bold blue]Method:[/bold blue] {result.method.upper()}
[bold blue]Lookup Time:[/bold blue] {result.lookup_time:.2f}s
[bold blue]Registrar:[/bold blue] {domain_info.registrar or '[dim]N/A[/dim]'}
[bold blue]Status:[/bold blue] {', '.join(domain_info.status) if domain_info.status else '[dim]N/A[/dim]'}
"""
    
    console.print(Panel(info_text, title="[bold green]Domain Information[/bold green]", border_style="green"))
    
    # Create dates table
    dates_table = Table(title="[bold]Important Dates[/bold]", box=box.ROUNDED)
    dates_table.add_column("Event", style="cyan")
    dates_table.add_column("Date", style="yellow")
    
    dates_table.add_row("Creation", format_date(domain_info.creation_date))
    dates_table.add_row("Expiration", format_date(domain_info.expiration_date))
    dates_table.add_row("Last Updated", format_date(domain_info.updated_date))
    
    console.print(dates_table)
    
    # Create name servers table
    if domain_info.name_servers:
        ns_table = Table(title="[bold]Name Servers[/bold]", box=box.ROUNDED)
        ns_table.add_column("Server", style="cyan")
        
        for ns in domain_info.name_servers:
            ns_table.add_row(ns)
        
        console.print(ns_table)
    
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
    
    # Show raw data if requested
    if domain_info.raw_data and len(domain_info.raw_data) < 1000:
        console.print("\n[bold]Raw Data:[/bold]")
        syntax = Syntax(domain_info.raw_data, "text", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Raw Data", border_style="blue"))


def display_bulk_results(results: BulkLookupResult):
    """Display bulk lookup results"""
    # Summary panel
    summary_text = f"""
[bold blue]Total Domains:[/bold blue] {results.total_domains}
[bold green]Successful:[/bold green] {results.successful_lookups}
[bold red]Failed:[/bold red] {results.failed_lookups}
[bold blue]Total Time:[/bold blue] {results.total_time:.2f}s
[bold blue]Average per Domain:[/bold blue] {results.average_time_per_domain:.2f}s
"""
    
    console.print(Panel(summary_text, title="[bold]Bulk Lookup Summary[/bold]", border_style="blue"))
    
    # Results table
    results_table = Table(title="[bold]Results[/bold]", box=box.ROUNDED)
    results_table.add_column("Domain", style="cyan")
    results_table.add_column("Status", style="green")
    results_table.add_column("Method", style="yellow")
    results_table.add_column("Time", style="blue")
    results_table.add_column("Registrar", style="magenta")
    
    for result in results.results:
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
):
    """Lookup a single domain"""
    async def _lookup():
        checker = DomainChecker(timeout=timeout)
        result = await checker.lookup_domain(domain, method, dig_record_type)
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
):
    """Lookup multiple domains"""
    async def _bulk():
        checker = DomainChecker(
            timeout=timeout,
            max_concurrent=max_concurrent,
            rate_limit=rate_limit
        )
        
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
):
    """Lookup domains from a file"""
    async def _file():
        checker = DomainChecker(
            timeout=timeout,
            max_concurrent=max_concurrent,
            rate_limit=rate_limit
        )
        
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
        
        display_bulk_results(results)
    
    asyncio.run(_file())


@app.command()
def dig(
    domain: str = typer.Argument(..., help="Domain name to lookup"),
    record_type: str = typer.Option("ANY", "--record", "-r", help="DNS record type: A, AAAA, MX, NS, SOA, TXT, ANY"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout in seconds"),
):
    """Perform DIG lookup for a domain"""
    async def _dig():
        checker = DomainChecker(timeout=timeout)
        result = await checker.dig_lookup(domain, record_type)
        display_domain_info(result)
    
    asyncio.run(_dig())


@app.command()
def reverse(
    ip: str = typer.Argument(..., help="IP address to lookup"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout in seconds"),
):
    """Perform reverse DNS lookup for an IP address"""
    async def _reverse():
        checker = DomainChecker(timeout=timeout)
        result = await checker.reverse_lookup(ip)
        display_domain_info(result)
    
    asyncio.run(_reverse())


@app.command()
def propagation(
    domain: str = typer.Argument(..., help="Domain name to check"),
    record_type: str = typer.Option("A", "--record", "-r", help="DNS record type: A, AAAA, MX, NS"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Timeout in seconds"),
):
    """Check DNS propagation across regional ISPs"""
    async def _propagation():
        checker = DomainChecker(timeout=timeout)
        
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
            command = typer.prompt("domain-check> ").strip()
            
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


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
