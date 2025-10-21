"""
DIG client for DNS lookups
"""

import asyncio
import subprocess
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import DomainInfo
from .exceptions import DigError


class DigClient:
    """Asynchronous DIG client for DNS lookups"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    async def lookup(self, domain: str, record_type: str = "ANY") -> DomainInfo:
        """
        Perform DIG lookup for a domain
        
        Args:
            domain: Domain name to lookup
            record_type: DNS record type (A, AAAA, MX, NS, SOA, TXT, ANY, etc.)
            
        Returns:
            DomainInfo object with parsed DIG data
        """
        try:
            loop = asyncio.get_event_loop()
            
            # If ANY is requested, query multiple record types in parallel
            if record_type.upper() == "ANY":
                record_types = ["A", "AAAA", "MX", "NS", "SOA", "TXT", "CNAME"]
                
                # Create tasks for parallel execution
                async def query_record_type(rt: str) -> tuple[str, str]:
                    try:
                        output = await loop.run_in_executor(
                            None, self._sync_dig_lookup, domain, rt
                        )
                        return rt, output.strip() if output.strip() else ""
                    except:
                        return rt, ""
                
                # Execute all record type queries in parallel
                tasks = [query_record_type(rt) for rt in record_types]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results and combine records
                all_records = []
                auth_nameservers = []
                seen_records = set()  # Track seen records to avoid duplicates
                
                for result in results:
                    if isinstance(result, Exception):
                        continue
                    rt, output = result
                    if output:
                        # Parse the output to check for CNAME records
                        lines = output.strip().split('\n')
                        has_cname = False
                        cname_target = None
                        
                        for line in lines:
                            line = line.strip()
                            if line and "CNAME" in line:
                                has_cname = True
                                # Extract CNAME target
                                parts = line.split()
                                if len(parts) >= 5:
                                    cname_target = parts[4].rstrip('.')
                                break
                        
                        # If this is a CNAME record, we should only show it once
                        if has_cname:
                            record_key = f"CNAME:{line}" if line else f"CNAME:{rt}"
                            if record_key not in seen_records:
                                all_records.append(f"=== {rt} Records ===")
                                all_records.append(output)
                                seen_records.add(record_key)
                        else:
                            # For non-CNAME records, add them normally
                            all_records.append(f"=== {rt} Records ===")
                            all_records.append(output)
                        
                        # Extract NS records for authoritative nameservers
                        if rt == "NS" and not has_cname:
                            auth_nameservers = self._parse_ns_records(output)
                
                # Combine all records
                dig_output = "\n".join(all_records) if all_records else ""
                
                return self._parse_dig_data(domain, dig_output, "ANY", auth_nameservers)
            
            else:
                # Single record type lookup
                dig_output = await loop.run_in_executor(
                    None, self._sync_dig_lookup, domain, record_type
                )
                
                # Also get authoritative name servers (unless we're already querying NS)
                auth_nameservers = []
                if record_type.upper() != "NS":
                    try:
                        ns_output = await loop.run_in_executor(
                            None, self._sync_dig_lookup, domain, "NS"
                        )
                        auth_nameservers = self._parse_ns_records(ns_output)
                    except:
                        pass
                
                return self._parse_dig_data(domain, dig_output, record_type, auth_nameservers)
            
        except Exception as e:
            return DomainInfo(
                domain=domain,
                source="dig",
                raw_data=f"Error: {str(e)}"
            )
    
    def _sync_dig_lookup(self, domain: str, record_type: str) -> str:
        """Synchronous DIG lookup"""
        try:
            # Build DIG command - use +noall +answer to get structured output
            if record_type.upper() == "ANY":
                cmd = ["dig", "+noall", "+answer", domain]
            else:
                cmd = ["dig", "+noall", "+answer", domain, record_type.upper()]
            
            # Execute DIG command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                raise DigError(domain, f"DIG command failed: {result.stderr}")
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise DigError(domain, f"DIG lookup timed out after {self.timeout} seconds")
        except FileNotFoundError:
            raise DigError(domain, "DIG command not found. Please install dig (bind-utils)")
        except Exception as e:
            raise DigError(domain, f"DIG lookup failed: {str(e)}")
    
    def _parse_ns_records(self, ns_output: str) -> List[str]:
        """Parse NS records from DIG output"""
        if not ns_output.strip():
            return []
        
        # Extract NS records from the output
        ns_records = []
        for line in ns_output.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith(';'):
                # Parse structured DNS record format: domain. TTL IN NS server.
                parts = line.split()
                if len(parts) >= 5 and parts[2] == "IN" and parts[3] == "NS":
                    # Extract just the server name
                    server = parts[4].rstrip('.')
                    if server:
                        ns_records.append(server)
                else:
                    # Fallback to simple format - just the server name
                    ns_record = line.rstrip('.')
                    if ns_record:
                        ns_records.append(ns_record)
        
        return ns_records
    
    def _parse_dig_data(self, domain: str, dig_output: str, record_type: str, auth_nameservers: List[str] = None) -> DomainInfo:
        """Parse DIG output into DomainInfo object"""
        if not dig_output.strip():
            return DomainInfo(
                domain=domain,
                source="dig",
                raw_data="No DNS records found"
            )
        
        # Parse different record types
        records = self._parse_records(dig_output, record_type)
        
        # Extract name servers (use auth_nameservers if provided, otherwise parse from records)
        name_servers = []
        if auth_nameservers:
            name_servers = auth_nameservers
        elif record_type.upper() in ["NS", "ANY"]:
            name_servers = [record.get("value", "") for record in records if record.get("type") == "NS"]
        
        # Extract MX records
        mx_records = []
        if record_type.upper() in ["MX", "ANY"]:
            mx_records = [record.get("value", "") for record in records if record.get("type") == "MX"]
        
        # Extract A records
        a_records = []
        if record_type.upper() in ["A", "ANY"]:
            a_records = [record.get("value", "") for record in records if record.get("type") == "A"]
        
        # Extract AAAA records
        aaaa_records = []
        if record_type.upper() in ["AAAA", "ANY"]:
            aaaa_records = [record.get("value", "") for record in records if record.get("type") == "AAAA"]
        
        # Extract TXT records
        txt_records = []
        if record_type.upper() in ["TXT", "ANY"]:
            txt_records = [record.get("value", "") for record in records if record.get("type") == "TXT"]
        
        # Extract SOA record
        soa_record = None
        if record_type.upper() in ["SOA", "ANY"]:
            soa_records = [record for record in records if record.get("type") == "SOA"]
            if soa_records:
                soa_record = soa_records[0].get("value")
        
        # Create contact information from SOA
        registrant = None
        if soa_record:
            # Parse SOA record for contact info
            soa_parts = soa_record.split()
            if len(soa_parts) >= 2:
                registrant = {
                    "name": "DNS Administrator",
                    "email": soa_parts[1].replace(".", "@", 1) if "." in soa_parts[1] else soa_parts[1]
                }
        
        return DomainInfo(
            domain=domain,
            registrar=None,  # DIG doesn't provide registrar info
            creation_date=None,  # DIG doesn't provide creation date
            expiration_date=None,  # DIG doesn't provide expiration date
            updated_date=None,  # DIG doesn't provide update date
            status=[],  # DIG doesn't provide status
            name_servers=name_servers,
            registrant=registrant,
            admin_contact=None,
            tech_contact=None,
            raw_data=dig_output,
            source="dig"
        )
    
    def _parse_records(self, dig_output: str, record_type: str) -> List[Dict[str, Any]]:
        """Parse DIG output into structured records"""
        records = []
        lines = dig_output.strip().split('\n')
        current_record_type = record_type
        
        for line in lines:
            if not line.strip():
                continue
            
            # Check if this is a section header
            if line.startswith("=== ") and line.endswith(" Records ==="):
                current_record_type = line.replace("=== ", "").replace(" Records ===", "")
                continue
            
            # Parse different record formats
            if record_type.upper() == "ANY":
                # Parse ANY record type with current section type
                record = self._parse_specific_record(line, current_record_type)
            else:
                # Parse specific record type
                record = self._parse_specific_record(line, record_type)
            
            if record:
                records.append(record)
        
        return records
    
    def _parse_any_record(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse ANY record type from DIG output"""
        # Format: domain. TTL IN TYPE value
        parts = line.split()
        if len(parts) < 4:
            return None
        
        domain = parts[0].rstrip('.')
        ttl = parts[1]
        record_class = parts[2]
        record_type = parts[3]
        value = ' '.join(parts[4:]) if len(parts) > 4 else ""
        
        return {
            "domain": domain,
            "ttl": ttl,
            "class": record_class,
            "type": record_type,
            "value": value
        }
    
    def _parse_specific_record(self, line: str, record_type: str) -> Optional[Dict[str, Any]]:
        """Parse specific record type from DIG output"""
        line = line.strip()
        if not line:
            return None
        
        # Try to parse structured DNS record format: domain. TTL IN TYPE value
        parts = line.split()
        if len(parts) >= 4 and parts[2] == "IN":
            # Structured format: domain. TTL IN TYPE value
            domain = parts[0].rstrip('.')
            ttl = parts[1]
            record_type_actual = parts[3]
            value = ' '.join(parts[4:]) if len(parts) > 4 else ""
            
            return {
                "domain": domain,
                "ttl": ttl,
                "type": record_type_actual,
                "value": value
            }
        else:
            # Fallback to simple value format
            return {
                "type": record_type.upper(),
                "value": line
            }
    
    async def lookup_multiple_types(self, domain: str, record_types: List[str]) -> Dict[str, DomainInfo]:
        """Lookup multiple record types for a domain in parallel"""
        async def lookup_single_type(record_type: str) -> tuple[str, DomainInfo]:
            try:
                result = await self.lookup(domain, record_type)
                return record_type, result
            except Exception as e:
                return record_type, DomainInfo(
                    domain=domain,
                    source="dig",
                    raw_data=f"Error: {str(e)}"
                )
        
        # Execute all lookups in parallel
        tasks = [lookup_single_type(rt) for rt in record_types]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert to dictionary
        results = {}
        for result in results_list:
            if isinstance(result, Exception):
                continue
            record_type, domain_info = result
            results[record_type] = domain_info
        
        return results
    
    async def reverse_lookup(self, ip: str) -> DomainInfo:
        """Perform reverse DNS lookup"""
        try:
            loop = asyncio.get_event_loop()
            dig_output = await loop.run_in_executor(
                None, self._sync_reverse_lookup, ip
            )
            
            return self._parse_reverse_lookup(ip, dig_output)
            
        except Exception as e:
            return DomainInfo(
                domain=ip,
                source="dig",
                raw_data=f"Error: {str(e)}"
            )
    
    def _sync_reverse_lookup(self, ip: str) -> str:
        """Synchronous reverse DNS lookup"""
        try:
            cmd = ["dig", "+short", "+noall", "+answer", "-x", ip]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                raise DigError(ip, f"Reverse lookup failed: {result.stderr}")
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise DigError(ip, f"Reverse lookup timed out after {self.timeout} seconds")
        except Exception as e:
            raise DigError(ip, f"Reverse lookup failed: {str(e)}")
    
    def _parse_reverse_lookup(self, ip: str, dig_output: str) -> DomainInfo:
        """Parse reverse lookup output"""
        if not dig_output.strip():
            return DomainInfo(
                domain=ip,
                source="dig",
                raw_data="No reverse DNS record found"
            )
        
        # Extract the hostname
        hostname = dig_output.strip().rstrip('.')
        
        return DomainInfo(
            domain=hostname,
            registrar=None,
            creation_date=None,
            expiration_date=None,
            updated_date=None,
            status=[],
            name_servers=[],
            registrant=None,
            admin_contact=None,
            tech_contact=None,
            raw_data=dig_output,
            source="dig"
        )
    
    async def query_with_nameserver(self, domain: str, record_type: str, nameserver: str, norecurse: bool = True) -> str:
        """
        Perform DIG lookup using a specific nameserver
        
        Args:
            domain: Domain name to lookup
            record_type: DNS record type (A, AAAA, MX, NS, SOA, TXT, ANY, etc.)
            nameserver: Specific nameserver to query (IP or hostname)
            norecurse: If True, use non-recursive queries (prevents recursive resolution)
            
        Returns:
            Raw DIG output as string
        """
        try:
            loop = asyncio.get_event_loop()
            dig_output = await loop.run_in_executor(
                None, self._sync_dig_lookup_with_ns, domain, record_type, nameserver, norecurse
            )
            return dig_output
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _sync_dig_lookup_with_ns(self, domain: str, record_type: str, nameserver: str, norecurse: bool = True) -> str:
        """Synchronous DIG lookup with specific nameserver"""
        try:
            # Build DIG command with specific nameserver - use same format as default resolvers
            # Use norecurse by default to prevent recursive resolution when querying custom nameservers
            # Include +comments so we can inspect flags (AA) in the header
            base_flags = ["+noadditional", "+noquestion", "+nocmd", "+nostats", "+comments"]
            if norecurse:
                base_flags.extend(["+norecurse", "+nosearch", "+noidnout"])
                
            if record_type.upper() == "ANY":
                cmd = ["dig"] + base_flags + [f"@{nameserver}", domain]
            else:
                cmd = ["dig"] + base_flags + [f"@{nameserver}", domain, record_type.upper()]
            
            # Execute DIG command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                raise DigError(domain, f"DIG command failed with {nameserver}: {result.stderr}")
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise DigError(domain, f"DIG lookup with {nameserver} timed out after {self.timeout} seconds")
        except FileNotFoundError:
            raise DigError(domain, "DIG command not found. Please install dig (bind-utils)")
        except Exception as e:
            raise DigError(domain, f"DIG lookup with {nameserver} failed: {str(e)}")