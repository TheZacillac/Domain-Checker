"""
RDAP client for domain lookups
Integrates with TheZacillac/rdap-cli framework
https://github.com/TheZacillac/rdap-cli
"""

import asyncio
import json
import ipaddress
import ssl
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import urllib.request
import urllib.error
from .models import DomainInfo

# IANA RDAP Bootstrap URLs (from TheZacillac/rdap-cli)
BOOTSTRAP_URLS = {
    'dns': 'https://data.iana.org/rdap/dns.json',
    'ipv4': 'https://data.iana.org/rdap/ipv4.json',
    'ipv6': 'https://data.iana.org/rdap/ipv6.json',
    'asn': 'https://data.iana.org/rdap/asn.json'
}


class RdapClient:
    """
    Asynchronous RDAP client
    Based on TheZacillac/rdap-cli framework
    https://github.com/TheZacillac/rdap-cli
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.bootstrap_cache: Dict[str, Any] = {}
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass
    
    async def fetch_url(self, url: str) -> Dict:
        """Fetch JSON data from a URL (async wrapper)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_fetch_url, url)
    
    def _sync_fetch_url(self, url: str) -> Dict:
        """Synchronous URL fetch"""
        try:
            # Create SSL context that doesn't verify certificates (for compatibility)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'DomainChecker-RDAP/1.0 (https://github.com/TheZacillac/rdap-cli)'}
            )
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP Error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"URL Error: {e.reason}")
        except Exception as e:
            raise Exception(f"Error fetching URL: {str(e)}")
    
    async def get_bootstrap(self, bootstrap_type: str) -> Dict:
        """Fetch and cache bootstrap data"""
        if bootstrap_type in self.bootstrap_cache:
            return self.bootstrap_cache[bootstrap_type]
        
        url = BOOTSTRAP_URLS.get(bootstrap_type)
        if not url:
            raise Exception(f"Unknown bootstrap type: {bootstrap_type}")
        
        data = await self.fetch_url(url)
        self.bootstrap_cache[bootstrap_type] = data
        return data
    
    def detect_query_type(self, query: str) -> Tuple[str, str]:
        """Detect the type of query (domain, IP, or ASN)"""
        query = query.strip()
        
        # Check if it's an ASN
        if query.upper().startswith('AS') and query[2:].isdigit():
            return 'asn', query[2:]
        
        # Check if it's an IP address
        try:
            ip = ipaddress.ip_address(query)
            if isinstance(ip, ipaddress.IPv4Address):
                return 'ipv4', query
            else:
                return 'ipv6', query
        except ValueError:
            pass
        
        # Assume it's a domain
        return 'dns', query.lower()
    
    async def find_rdap_server(self, query: str, query_type: str) -> Optional[str]:
        """Find the appropriate RDAP server for a query"""
        bootstrap = await self.get_bootstrap(query_type)
        services = bootstrap.get('services', [])
        
        if query_type == 'dns':
            # Extract TLD from domain
            tld = query.split('.')[-1].lower()
            for service in services:
                if tld in [t.lower() for t in service[0]]:
                    return service[1][0]  # Return first server URL
        
        elif query_type in ['ipv4', 'ipv6']:
            # Find IP range that contains the query IP
            ip = ipaddress.ip_address(query)
            for service in services:
                for range_str in service[0]:
                    network = ipaddress.ip_network(range_str)
                    if ip in network:
                        return service[1][0]
        
        elif query_type == 'asn':
            # Find ASN range
            asn = int(query.replace('AS', '').replace('as', ''))
            for service in services:
                for range_str in service[0]:
                    if '-' in range_str:
                        start, end = map(int, range_str.split('-'))
                        if start <= asn <= end:
                            return service[1][0]
                    else:
                        if asn == int(range_str):
                            return service[1][0]
        
        return None
    
    async def query_rdap(self, query: str) -> Dict:
        """Perform an RDAP query"""
        query_type, normalized_query = self.detect_query_type(query)
        
        # Find the appropriate RDAP server
        server = await self.find_rdap_server(normalized_query, query_type)
        if not server:
            raise Exception(f"No RDAP server found for {query}")
        
        # Build the query URL
        if query_type == 'dns':
            url = f"{server.rstrip('/')}/domain/{normalized_query}"
        elif query_type in ['ipv4', 'ipv6']:
            url = f"{server.rstrip('/')}/ip/{normalized_query}"
        elif query_type == 'asn':
            url = f"{server.rstrip('/')}/autnum/{normalized_query}"
        else:
            raise Exception(f"Unsupported query type: {query_type}")
        
        # Perform the query
        return await self.fetch_url(url)
    
    async def lookup(self, domain: str) -> DomainInfo:
        """
        Perform RDAP lookup for a domain
        
        Args:
            domain: Domain name to lookup
            
        Returns:
            DomainInfo object with parsed RDAP data
        """
        try:
            # Perform RDAP query using the framework
            rdap_data = await self.query_rdap(domain)
            
            # Parse the response
            return self._parse_rdap_data(domain, rdap_data)
            
        except Exception as e:
            # If RDAP fails, return minimal info
            return DomainInfo(
                domain=domain,
                source="rdap",
                raw_data=f"Error: {str(e)}"
            )
    
    def _parse_rdap_data(self, domain: str, rdap_data: Dict) -> DomainInfo:
        """Parse RDAP response into DomainInfo"""
        try:
            # Extract basic information
            domain_name = rdap_data.get('ldhName') or rdap_data.get('unicodeName') or domain
            status = rdap_data.get('status', [])
            
            # Extract dates
            events = rdap_data.get('events', [])
            creation_date = None
            expiration_date = None
            updated_date = None
            
            for event in events:
                event_action = event.get('eventAction', '').lower()
                event_date_str = event.get('eventDate', '')
                
                try:
                    event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                except:
                    continue
                
                if 'registration' in event_action:
                    creation_date = event_date
                elif 'expiration' in event_action:
                    expiration_date = event_date
                elif 'last changed' in event_action or 'last update' in event_action:
                    updated_date = event_date
            
            # Extract name servers
            nameservers = []
            for ns in rdap_data.get('nameservers', []):
                ns_name = ns.get('ldhName', '')
                if ns_name:
                    nameservers.append(ns_name)
            
            # Extract registrar and entities
            registrar = None
            registrant = None
            admin_contact = None
            tech_contact = None
            
            entities = rdap_data.get('entities', [])
            for entity in entities:
                roles = entity.get('roles', [])
                
                # Extract vCard data if present
                vcard_data = None
                if 'vcardArray' in entity and len(entity['vcardArray']) > 1:
                    vcard_data = self._parse_vcard(entity['vcardArray'][1])
                
                # Assign based on role
                if 'registrar' in roles:
                    # Try to get registrar name from various sources
                    if vcard_data:
                        registrar = vcard_data.get('name') or vcard_data.get('organization')
                    if not registrar and 'publicIds' in entity:
                        # Some registrars have public IDs with the name
                        for public_id in entity['publicIds']:
                            if public_id.get('type') == 'IANA Registrar ID':
                                registrar = f"Registrar ID: {public_id.get('identifier')}"
                                break
                    if not registrar:
                        registrar = entity.get('handle')
                elif 'registrant' in roles:
                    registrant = vcard_data
                elif 'administrative' in roles:
                    admin_contact = vcard_data
                elif 'technical' in roles:
                    tech_contact = vcard_data
            
            return DomainInfo(
                domain=domain_name,
                registrar=registrar,
                creation_date=creation_date,
                expiration_date=expiration_date,
                updated_date=updated_date,
                status=status,
                name_servers=nameservers,
                registrant=registrant,
                admin_contact=admin_contact,
                tech_contact=tech_contact,
                raw_data=json.dumps(rdap_data, indent=2),
                source="rdap"
            )
            
        except Exception as e:
            return DomainInfo(
                domain=domain,
                source="rdap",
                raw_data=f"Error parsing RDAP data: {str(e)}\n\n{json.dumps(rdap_data, indent=2)}"
            )
    
    def _parse_vcard(self, vcard_array: list) -> Optional[Dict[str, str]]:
        """Parse vCard data from RDAP response"""
        if not vcard_array:
            return None
        
        result = {}
        
        for item in vcard_array:
            if len(item) < 4:
                continue
            
            field_name = item[0]
            value = item[3]
            
            if field_name == 'fn':  # Full name
                result['name'] = value
                result['fn'] = value  # Also store as 'fn' for compatibility
            elif field_name == 'org':  # Organization
                result['organization'] = value
            elif field_name == 'email':
                result['email'] = value
            elif field_name == 'tel':
                result['phone'] = value
            elif field_name == 'adr' and isinstance(value, list):  # Address
                addr_parts = [p for p in value if p]
                if addr_parts:
                    result['address'] = ', '.join(addr_parts)
        
        return result if result else None