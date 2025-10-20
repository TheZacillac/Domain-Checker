"""
Core domain checker with async bulk processing
"""

import asyncio
import time
from typing import List, Optional, Union
from asyncio_throttle import Throttler

from .models import DomainInfo, LookupResult, BulkLookupResult
from .whois_client import WhoisClient
from .rdap_client import RdapClient
from .dig_client import DigClient
from .propagation_checker import DNSPropagationChecker


class DomainChecker:
    """Main domain checker class with async bulk processing"""
    
    def __init__(self, 
                 timeout: int = 30,
                 max_concurrent: int = 10,
                 rate_limit: float = 1.0):
        """
        Initialize domain checker
        
        Args:
            timeout: Timeout for individual lookups in seconds
            max_concurrent: Maximum concurrent lookups
            rate_limit: Rate limit in requests per second
        """
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        
        self.whois_client = WhoisClient(timeout=timeout)
        self.rdap_client = RdapClient(timeout=timeout)
        self.dig_client = DigClient(timeout=timeout)
        self.propagation_checker = DNSPropagationChecker(timeout=timeout)
        self.throttler = Throttler(rate_limit=rate_limit)
    
    async def lookup_domain(self, 
                           domain: str, 
                           method: str = "auto",
                           dig_record_type: str = "ANY") -> LookupResult:
        """
        Lookup a single domain
        
        Args:
            domain: Domain name to lookup
            method: Lookup method ("whois", "rdap", "dig", or "auto")
            dig_record_type: DNS record type for DIG lookups ("A", "AAAA", "MX", "NS", "SOA", "TXT", "ANY")
            
        Returns:
            LookupResult with domain information
        """
        start_time = time.time()
        
        try:
            if method == "auto":
                # Try RDAP first, fallback to WHOIS
                try:
                    async with self.rdap_client:
                        domain_info = await self.rdap_client.lookup(domain)
                        if domain_info.raw_data and "Error:" not in domain_info.raw_data:
                            lookup_time = time.time() - start_time
                            result = LookupResult(
                                domain=domain,
                                success=True,
                                data=domain_info,
                                lookup_time=lookup_time,
                                method="rdap"
                            )
                            result.registration_status = self._determine_registration_status(result)
                            return result
                except Exception:
                    pass
                
                # Fallback to WHOIS
                domain_info = await self.whois_client.lookup(domain)
                lookup_time = time.time() - start_time
                result = LookupResult(
                    domain=domain,
                    success=True,
                    data=domain_info,
                    lookup_time=lookup_time,
                    method="whois"
                )
                result.registration_status = self._determine_registration_status(result)
                return result
            
            elif method == "rdap":
                async with self.rdap_client:
                    domain_info = await self.rdap_client.lookup(domain)
                    lookup_time = time.time() - start_time
                    result = LookupResult(
                        domain=domain,
                        success=True,
                        data=domain_info,
                        lookup_time=lookup_time,
                        method="rdap"
                    )
                    result.registration_status = self._determine_registration_status(result)
                    return result
            
            elif method == "whois":
                domain_info = await self.whois_client.lookup(domain)
                lookup_time = time.time() - start_time
                result = LookupResult(
                    domain=domain,
                    success=True,
                    data=domain_info,
                    lookup_time=lookup_time,
                    method="whois"
                )
                result.registration_status = self._determine_registration_status(result)
                return result
            
            elif method == "dig":
                domain_info = await self.dig_client.lookup(domain, dig_record_type)
                lookup_time = time.time() - start_time
                result = LookupResult(
                    domain=domain,
                    success=True,
                    data=domain_info,
                    lookup_time=lookup_time,
                    method="dig"
                )
                result.registration_status = self._determine_registration_status(result)
                return result
            
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            lookup_time = time.time() - start_time
            result = LookupResult(
                domain=domain,
                success=False,
                error=str(e),
                lookup_time=lookup_time,
                method=method
            )
            result.registration_status = self._determine_registration_status(result)
            return result
    
    async def lookup_domains_bulk(self, 
                                 domains: List[str], 
                                 method: str = "auto",
                                 dig_record_type: str = "ANY") -> BulkLookupResult:
        """
        Lookup multiple domains with rate limiting and concurrency control
        
        Args:
            domains: List of domain names to lookup
            method: Lookup method ("whois", "rdap", "dig", or "auto")
            dig_record_type: DNS record type for DIG lookups
            
        Returns:
            BulkLookupResult with all lookup results
        """
        start_time = time.time()
        results = []
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def lookup_with_semaphore(domain: str) -> LookupResult:
            async with semaphore:
                async with self.throttler:
                    return await self.lookup_domain(domain, method, dig_record_type)
        
        # Execute all lookups concurrently
        tasks = [lookup_with_semaphore(domain) for domain in domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                lookup_result = LookupResult(
                    domain=domains[i],
                    success=False,
                    error=str(result),
                    lookup_time=0.0,
                    method=method
                )
                lookup_result.registration_status = self._determine_registration_status(lookup_result)
                processed_results.append(lookup_result)
            else:
                processed_results.append(result)
        
        total_time = time.time() - start_time
        successful = sum(1 for r in processed_results if r.success)
        failed = len(processed_results) - successful
        
        return BulkLookupResult(
            total_domains=len(domains),
            successful_lookups=successful,
            failed_lookups=failed,
            results=processed_results,
            total_time=total_time,
            average_time_per_domain=total_time / len(domains) if domains else 0.0
        )
    
    async def lookup_domains_from_file(self, 
                                     file_path: str, 
                                     method: str = "auto",
                                     dig_record_type: str = "ANY") -> BulkLookupResult:
        """
        Lookup domains from a text file (one domain per line)
        
        Args:
            file_path: Path to file containing domains
            method: Lookup method ("whois", "rdap", "dig", or "auto")
            dig_record_type: DNS record type for DIG lookups
            
        Returns:
            BulkLookupResult with all lookup results
        """
        try:
            with open(file_path, 'r') as f:
                domains = [line.strip() for line in f if line.strip()]
            
            return await self.lookup_domains_bulk(domains, method, dig_record_type)
            
        except FileNotFoundError:
            return BulkLookupResult(
                total_domains=0,
                successful_lookups=0,
                failed_lookups=0,
                results=[],
                total_time=0.0,
                average_time_per_domain=0.0
            )
    
    async def dig_lookup(self, domain: str, record_type: str = "ANY") -> LookupResult:
        """
        Perform DIG lookup for a domain
        
        Args:
            domain: Domain name to lookup
            record_type: DNS record type ("A", "AAAA", "MX", "NS", "SOA", "TXT", "ANY")
            
        Returns:
            LookupResult with DNS information
        """
        return await self.lookup_domain(domain, "dig", record_type)
    
    async def reverse_lookup(self, ip: str) -> LookupResult:
        """
        Perform reverse DNS lookup for an IP address
        
        Args:
            ip: IP address to lookup
            
        Returns:
            LookupResult with reverse DNS information
        """
        start_time = time.time()
        
        try:
            domain_info = await self.dig_client.reverse_lookup(ip)
            lookup_time = time.time() - start_time
            return LookupResult(
                domain=ip,
                success=True,
                data=domain_info,
                lookup_time=lookup_time,
                method="dig"
            )
        except Exception as e:
            lookup_time = time.time() - start_time
            return LookupResult(
                domain=ip,
                success=False,
                error=str(e),
                lookup_time=lookup_time,
                method="dig"
            )
    
    async def check_propagation(self, domain: str, record_type: str = "A"):
        """
        Check DNS propagation across regional ISPs
        
        Args:
            domain: Domain name to check
            record_type: DNS record type (A, AAAA, MX, NS, etc.)
            
        Returns:
            PropagationSummary with results from all resolvers
        """
        return await self.propagation_checker.check_propagation(domain, record_type)
    
    async def compare_methods(self, domain: str) -> dict:
        """
        Compare WHOIS and RDAP results for a domain
        
        Args:
            domain: Domain name to compare
            
        Returns:
            Dictionary with comparison results
        """
        whois_result = await self.lookup_domain(domain, "whois")
        rdap_result = await self.lookup_domain(domain, "rdap")
        
        return {
            "domain": domain,
            "whois": whois_result,
            "rdap": rdap_result,
            "comparison": {
                "whois_success": whois_result.success,
                "rdap_success": rdap_result.success,
                "whois_time": whois_result.lookup_time,
                "rdap_time": rdap_result.lookup_time,
                "data_available": {
                    "whois": whois_result.data is not None,
                    "rdap": rdap_result.data is not None
                }
            }
        }
    
    def _determine_registration_status(self, result: LookupResult) -> str:
        """
        Determine the registration status of a domain based on lookup results
        
        Args:
            result: LookupResult from domain lookup
            
        Returns:
            Registration status: "registered", "not_registered", or "possibly_registered"
        """
        if not result.success or not result.data:
            return "not_registered"
        
        domain_info = result.data
        
        # Check for clear indicators of registration
        if domain_info.registrar:
            return "registered"
        
        if domain_info.creation_date:
            return "registered"
        
        if domain_info.expiration_date:
            return "registered"
        
        if domain_info.name_servers:
            return "registered"
        
        # Check for indicators of non-registration
        if result.error:
            error_lower = result.error.lower()
            if any(phrase in error_lower for phrase in [
                "no match", "not found", "no entries found", 
                "no data found", "domain not found", "not registered",
                "no whois data available", "no information available"
            ]):
                return "not_registered"
        
        # Check raw data for registration indicators
        if domain_info.raw_data:
            raw_lower = domain_info.raw_data.lower()
            
            # Clear indicators of registration
            if any(phrase in raw_lower for phrase in [
                "registrar:", "creation date:", "expiration date:",
                "name server:", "status: active", "status: ok",
                "domain name:", "registry domain id:"
            ]):
                return "registered"
            
            # Clear indicators of non-registration
            if any(phrase in raw_lower for phrase in [
                "no match", "not found", "no entries found",
                "no data found", "domain not found", "not registered",
                "no whois data available", "no information available",
                "no data available"
            ]):
                return "not_registered"
        
        # If we have some data but can't determine clearly
        return "possibly_registered"