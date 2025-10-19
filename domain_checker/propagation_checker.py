"""
DNS Propagation Checker - Check DNS resolution across regional ISPs
"""

import asyncio
import subprocess
from typing import List, Dict, Optional, Any
from datetime import datetime
from .models import DomainInfo


class PropagationResult:
    """Result from a single DNS resolver"""
    
    def __init__(self, 
                 resolver_name: str,
                 resolver_ip: str,
                 location: str,
                 domain: str,
                 record_type: str,
                 resolved_ips: List[str],
                 success: bool,
                 error: Optional[str] = None,
                 lookup_time: float = 0.0):
        self.resolver_name = resolver_name
        self.resolver_ip = resolver_ip
        self.location = location
        self.domain = domain
        self.record_type = record_type
        self.resolved_ips = resolved_ips
        self.success = success
        self.error = error
        self.lookup_time = lookup_time
        self.timestamp = datetime.now()


class PropagationSummary:
    """Summary of propagation check across all resolvers"""
    
    def __init__(self, 
                 domain: str,
                 record_type: str,
                 results: List[PropagationResult],
                 total_time: float):
        self.domain = domain
        self.record_type = record_type
        self.results = results
        self.total_time = total_time
        
        # Calculate statistics
        self.total_resolvers = len(results)
        self.successful = sum(1 for r in results if r.success)
        self.failed = self.total_resolvers - self.successful
        
        # Find unique IPs
        self.unique_ips = set()
        for result in results:
            if result.success:
                self.unique_ips.update(result.resolved_ips)
        
        # Check if fully propagated (all resolvers return same IPs)
        if self.successful > 0:
            successful_results = [r for r in results if r.success]
            first_ips = set(successful_results[0].resolved_ips)
            self.fully_propagated = all(
                set(r.resolved_ips) == first_ips 
                for r in successful_results
            )
        else:
            self.fully_propagated = False
        
        # Calculate propagation percentage
        if self.unique_ips and self.successful > 0:
            # Most common IP set
            ip_counts = {}
            for result in results:
                if result.success:
                    ip_key = tuple(sorted(result.resolved_ips))
                    ip_counts[ip_key] = ip_counts.get(ip_key, 0) + 1
            
            if ip_counts:
                most_common_count = max(ip_counts.values())
                self.propagation_percentage = (most_common_count / self.total_resolvers) * 100
            else:
                self.propagation_percentage = 0.0
        else:
            self.propagation_percentage = 0.0


# Popular DNS resolvers from different regions/ISPs
GLOBAL_DNS_RESOLVERS = [
    # North America
    {"name": "Google Public DNS (Primary)", "ip": "8.8.8.8", "location": "Global"},
    {"name": "Google Public DNS (Secondary)", "ip": "8.8.4.4", "location": "Global"},
    {"name": "Cloudflare DNS (Primary)", "ip": "1.1.1.1", "location": "Global"},
    {"name": "Cloudflare DNS (Secondary)", "ip": "1.0.0.1", "location": "Global"},
    {"name": "Quad9 DNS", "ip": "9.9.9.9", "location": "Global"},
    {"name": "OpenDNS (Primary)", "ip": "208.67.222.222", "location": "Global"},
    {"name": "OpenDNS (Secondary)", "ip": "208.67.220.220", "location": "Global"},
    
    # Level 3 / CenturyLink
    {"name": "Level3 DNS (Primary)", "ip": "4.2.2.1", "location": "North America"},
    {"name": "Level3 DNS (Secondary)", "ip": "4.2.2.2", "location": "North America"},
    
    # Comcast
    {"name": "Comcast DNS", "ip": "75.75.75.75", "location": "North America"},
    
    # AT&T
    {"name": "AT&T DNS", "ip": "68.94.156.1", "location": "North America"},
    
    # Europe
    {"name": "DNS.WATCH (Primary)", "ip": "84.200.69.80", "location": "Europe"},
    {"name": "DNS.WATCH (Secondary)", "ip": "84.200.70.40", "location": "Europe"},
    
    # Asia
    {"name": "Neustar DNS", "ip": "156.154.70.1", "location": "Global"},
    {"name": "Norton ConnectSafe", "ip": "199.85.126.10", "location": "Global"},
    
    # AdGuard DNS
    {"name": "AdGuard DNS", "ip": "94.140.14.14", "location": "Global"},
    
    # Verisign
    {"name": "Verisign DNS", "ip": "64.6.64.6", "location": "Global"},
    
    # FreeDNS
    {"name": "FreeDNS", "ip": "37.235.1.174", "location": "Europe"},
    
    # Alternate DNS
    {"name": "Alternate DNS", "ip": "76.76.19.19", "location": "North America"},
    
    # CleanBrowsing
    {"name": "CleanBrowsing", "ip": "185.228.168.9", "location": "Global"},
]


class DNSPropagationChecker:
    """Check DNS propagation across multiple resolvers"""
    
    def __init__(self, timeout: int = 10, custom_resolvers: Optional[List[Dict]] = None):
        """
        Initialize propagation checker
        
        Args:
            timeout: Timeout for each DNS query in seconds
            custom_resolvers: Optional list of custom resolvers to use
        """
        self.timeout = timeout
        self.resolvers = custom_resolvers if custom_resolvers else GLOBAL_DNS_RESOLVERS
    
    async def check_propagation(self, 
                                domain: str, 
                                record_type: str = "A") -> PropagationSummary:
        """
        Check DNS propagation across all resolvers
        
        Args:
            domain: Domain name to check
            record_type: DNS record type (A, AAAA, MX, NS, etc.)
            
        Returns:
            PropagationSummary with results from all resolvers
        """
        start_time = asyncio.get_event_loop().time()
        
        # Create tasks for all resolvers
        tasks = [
            self._query_resolver(resolver, domain, record_type)
            for resolver in self.resolvers
        ]
        
        # Execute all queries concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                # Create failed result
                valid_results.append(PropagationResult(
                    resolver_name="Unknown",
                    resolver_ip="Unknown",
                    location="Unknown",
                    domain=domain,
                    record_type=record_type,
                    resolved_ips=[],
                    success=False,
                    error=str(result)
                ))
            else:
                valid_results.append(result)
        
        total_time = asyncio.get_event_loop().time() - start_time
        
        return PropagationSummary(
            domain=domain,
            record_type=record_type,
            results=valid_results,
            total_time=total_time
        )
    
    async def _query_resolver(self, 
                             resolver: Dict[str, str],
                             domain: str,
                             record_type: str) -> PropagationResult:
        """Query a single DNS resolver"""
        import time
        start_time = time.time()
        
        try:
            # Run dig command against specific resolver
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._sync_dig_query,
                resolver["ip"],
                domain,
                record_type
            )
            
            lookup_time = time.time() - start_time
            
            # Parse result
            ips = self._parse_dig_output(result, record_type)
            
            return PropagationResult(
                resolver_name=resolver["name"],
                resolver_ip=resolver["ip"],
                location=resolver["location"],
                domain=domain,
                record_type=record_type,
                resolved_ips=ips,
                success=True,
                lookup_time=lookup_time
            )
            
        except Exception as e:
            lookup_time = time.time() - start_time
            return PropagationResult(
                resolver_name=resolver["name"],
                resolver_ip=resolver["ip"],
                location=resolver["location"],
                domain=domain,
                record_type=record_type,
                resolved_ips=[],
                success=False,
                error=str(e),
                lookup_time=lookup_time
            )
    
    def _sync_dig_query(self, resolver_ip: str, domain: str, record_type: str) -> str:
        """Synchronous DIG query against specific resolver"""
        try:
            cmd = ["dig", f"@{resolver_ip}", "+short", "+time=5", "+tries=1", domain, record_type.upper()]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Query timeout after {self.timeout}s")
        except FileNotFoundError:
            raise Exception("DIG command not found")
        except Exception as e:
            raise Exception(f"Query failed: {str(e)}")
    
    def _parse_dig_output(self, output: str, record_type: str) -> List[str]:
        """Parse DIG output to extract IPs/records"""
        if not output or not output.strip():
            return []
        
        lines = output.strip().split('\n')
        results = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(';'):
                # For MX records, skip the priority number
                if record_type.upper() == "MX" and ' ' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        results.append(parts[1])
                else:
                    results.append(line)
        
        return results
    
    def get_resolvers_by_location(self, location: str) -> List[Dict]:
        """Get resolvers for a specific location"""
        return [r for r in self.resolvers if r["location"].lower() == location.lower()]
    
    def add_custom_resolver(self, name: str, ip: str, location: str = "Custom"):
        """Add a custom resolver to the list"""
        self.resolvers.append({
            "name": name,
            "ip": ip,
            "location": location
        })
    
    def get_summary_stats(self, summary: PropagationSummary) -> Dict[str, Any]:
        """Get statistics from propagation summary"""
        return {
            "domain": summary.domain,
            "record_type": summary.record_type,
            "total_resolvers": summary.total_resolvers,
            "successful": summary.successful,
            "failed": summary.failed,
            "unique_ips": list(summary.unique_ips),
            "fully_propagated": summary.fully_propagated,
            "propagation_percentage": round(summary.propagation_percentage, 1),
            "total_time": round(summary.total_time, 2)
        }
