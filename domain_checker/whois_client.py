"""
WHOIS client for domain lookups
"""

import asyncio
import socket
from datetime import datetime
from typing import Optional, Dict, Any, List
import whois
from .models import DomainInfo


class WhoisClient:
    """Asynchronous WHOIS client"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    async def lookup(self, domain: str) -> DomainInfo:
        """
        Perform WHOIS lookup for a domain
        
        Args:
            domain: Domain name to lookup
            
        Returns:
            DomainInfo object with parsed WHOIS data
        """
        try:
            # Run WHOIS lookup in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            whois_data = await loop.run_in_executor(
                None, self._sync_whois_lookup, domain
            )
            
            return self._parse_whois_data(domain, whois_data)
            
        except Exception as e:
            # If WHOIS fails, return minimal info
            return DomainInfo(
                domain=domain,
                source="whois",
                raw_data=f"Error: {str(e)}"
            )
    
    def _sync_whois_lookup(self, domain: str) -> Optional[whois.WhoisEntry]:
        """Synchronous WHOIS lookup"""
        try:
            return whois.whois(domain)
        except Exception:
            return None
    
    def _parse_whois_data(self, domain: str, whois_data: Optional[whois.WhoisEntry]) -> DomainInfo:
        """Parse WHOIS data into DomainInfo object"""
        if not whois_data:
            return DomainInfo(
                domain=domain,
                source="whois",
                raw_data="No WHOIS data available"
            )
        
        # Extract dates
        creation_date = self._parse_date(whois_data.creation_date)
        expiration_date = self._parse_date(whois_data.expiration_date)
        updated_date = self._parse_date(whois_data.updated_date)
        
        # Extract name servers
        name_servers = []
        if whois_data.name_servers:
            if isinstance(whois_data.name_servers, list):
                name_servers = [str(ns).lower() for ns in whois_data.name_servers]
            else:
                name_servers = [str(whois_data.name_servers).lower()]
        
        # Extract status
        status = []
        if whois_data.status:
            if isinstance(whois_data.status, list):
                status = [str(s) for s in whois_data.status]
            else:
                status = [str(whois_data.status)]
        
        # Extract contact information
        registrant = self._extract_contact_info(whois_data.registrant)
        admin_contact = self._extract_contact_info(whois_data.admin)
        tech_contact = self._extract_contact_info(whois_data.tech)
        
        
        return DomainInfo(
            domain=domain,
            registrar=whois_data.registrar,
            creation_date=creation_date,
            expiration_date=expiration_date,
            updated_date=updated_date,
            status=status,
            name_servers=name_servers,
            registrant=registrant,
            admin_contact=admin_contact,
            tech_contact=tech_contact,
            raw_data=str(whois_data),
            source="whois"
        )
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse date from various formats"""
        if not date_value:
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, list) and date_value:
            date_value = date_value[0]
        
        if isinstance(date_value, str):
            try:
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d-%b-%Y', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        return datetime.strptime(date_value, fmt)
                    except ValueError:
                        continue
            except Exception:
                pass
        
        return None
    
    def _extract_contact_info(self, contact_data: Any) -> Optional[Dict[str, Any]]:
        """Extract contact information from WHOIS data"""
        if not contact_data:
            return None
        
        if isinstance(contact_data, dict):
            return {k: v for k, v in contact_data.items() if v is not None}
        
        if isinstance(contact_data, str):
            return {"raw": contact_data}
        
        return {"raw": str(contact_data)}
    
