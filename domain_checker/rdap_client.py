"""
RDAP client for domain lookups
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
from .models import DomainInfo
from .connection_pool import get_global_pool


class RdapClient:
    """Asynchronous RDAP client"""
    
    def __init__(self, timeout: int = 30, use_connection_pool: bool = True):
        self.timeout = timeout
        self.use_connection_pool = use_connection_pool
        self.session: Optional[aiohttp.ClientSession] = None
        self._pool = get_global_pool() if use_connection_pool else None
        
        # Common RDAP bootstrap servers
        self.bootstrap_servers = [
            "https://rdap.verisign.com/",
            "https://rdap.arin.net/",
            "https://rdap.afrinic.net/",
            "https://rdap.apnic.net/",
            "https://rdap.lacnic.net/",
            "https://rdap.ripe.net/",
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def lookup(self, domain: str) -> DomainInfo:
        """
        Perform RDAP lookup for a domain
        
        Args:
            domain: Domain name to lookup
            
        Returns:
            DomainInfo object with parsed RDAP data
        """
        # Use connection pool if available
        if self.use_connection_pool and self._pool:
            self.session = await self._pool.get_session()
        elif not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        
        try:
            # Try to find the appropriate RDAP server
            rdap_server = await self._find_rdap_server(domain)
            if not rdap_server:
                return DomainInfo(
                    domain=domain,
                    source="rdap",
                    raw_data="No RDAP server found for domain"
                )
            
            # Perform RDAP lookup
            rdap_data = await self._fetch_rdap_data(rdap_server, domain)
            if not rdap_data:
                return DomainInfo(
                    domain=domain,
                    source="rdap",
                    raw_data="No RDAP data available"
                )
            
            return self._parse_rdap_data(domain, rdap_data)
            
        except Exception as e:
            return DomainInfo(
                domain=domain,
                source="rdap",
                raw_data=f"Error: {str(e)}"
            )
    
    async def _find_rdap_server(self, domain: str) -> Optional[str]:
        """Find the appropriate RDAP server for a domain"""
        # For now, use a simple approach - try common servers
        # In a production system, you'd want to use the RDAP bootstrap service
        
        # Extract TLD
        tld = domain.split('.')[-1].lower()
        
        # Map common TLDs to their RDAP servers
        tld_servers = {
            'com': 'https://rdap.verisign.com/',
            'net': 'https://rdap.verisign.com/',
            'org': 'https://rdap.publicinterestregistry.net/',
            'info': 'https://rdap.afilias.net/',
            'biz': 'https://rdap.neustar.biz/',
            'us': 'https://rdap.verisign.com/',
            'uk': 'https://rdap.nominet.uk/',
            'de': 'https://rdap.denic.de/',
            'fr': 'https://rdap.afnic.fr/',
            'it': 'https://rdap.nic.it/',
            'es': 'https://rdap.nic.es/',
            'nl': 'https://rdap.sidn.nl/',
            'be': 'https://rdap.dns.be/',
            'ch': 'https://rdap.nic.ch/',
            'at': 'https://rdap.nic.at/',
            'se': 'https://rdap.iis.se/',
            'no': 'https://rdap.norid.no/',
            'dk': 'https://rdap.dk-hostmaster.dk/',
            'fi': 'https://rdap.traficom.fi/',
            'pl': 'https://rdap.dns.pl/',
            'cz': 'https://rdap.nic.cz/',
            'sk': 'https://rdap.sk-nic.sk/',
            'hu': 'https://rdap.nic.hu/',
            'ro': 'https://rdap.rotld.ro/',
            'bg': 'https://rdap.register.bg/',
            'hr': 'https://rdap.dns.hr/',
            'si': 'https://rdap.arnes.si/',
            'ee': 'https://rdap.tld.ee/',
            'lv': 'https://rdap.nic.lv/',
            'lt': 'https://rdap.domreg.lt/',
            'ie': 'https://rdap.weare.ie/',
            'pt': 'https://rdap.dns.pt/',
            'gr': 'https://rdap.forth.gr/',
            'cy': 'https://rdap.nic.cy/',
            'mt': 'https://rdap.nic.org.mt/',
            'lu': 'https://rdap.dns.lu/',
            'li': 'https://rdap.nic.li/',
            'is': 'https://rdap.isnic.is/',
            'fo': 'https://rdap.arnes.si/',
            'gl': 'https://rdap.arnes.si/',
            'ax': 'https://rdap.aland.fi/',
            'ad': 'https://rdap.nic.ad/',
            'mc': 'https://rdap.nic.mc/',
            'sm': 'https://rdap.nic.sm/',
            'va': 'https://rdap.nic.va/',
            'gi': 'https://rdap.nic.gi/',
            'gg': 'https://rdap.channelisles.net/',
            'je': 'https://rdap.channelisles.net/',
            'im': 'https://rdap.nic.im/',
            'co': 'https://rdap.co/',
            'ac': 'https://rdap.nic.ac/',
            'me': 'https://rdap.nic.me/',
            'tv': 'https://rdap.tv/',
            'cc': 'https://rdap.verisign.com/',
            'mobi': 'https://rdap.afilias.net/',
            'name': 'https://rdap.verisign.com/',
            'pro': 'https://rdap.afilias.net/',
            'aero': 'https://rdap.information.aero/',
            'coop': 'https://rdap.nic.coop/',
            'museum': 'https://rdap.museum/',
            'travel': 'https://rdap.travel/',
            'jobs': 'https://rdap.employmedia.com/',
            'cat': 'https://rdap.cat/',
            'tel': 'https://rdap.tel/',
            'asia': 'https://rdap.asia/',
            'post': 'https://rdap.post/',
            'xxx': 'https://rdap.icmregistry.com/',
            'arpa': 'https://rdap.iana.org/',
        }
        
        return tld_servers.get(tld, 'https://rdap.verisign.com/')
    
    async def _fetch_rdap_data(self, server: str, domain: str) -> Optional[Dict[str, Any]]:
        """Fetch RDAP data from server"""
        url = urljoin(server, f"domain/{domain}")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except Exception:
            return None
    
    def _parse_rdap_data(self, domain: str, rdap_data: Dict[str, Any]) -> DomainInfo:
        """Parse RDAP data into DomainInfo object"""
        # Extract basic information
        registrar = None
        creation_date = None
        expiration_date = None
        updated_date = None
        status = []
        name_servers = []
        registrant = None
        admin_contact = None
        tech_contact = None
        
        # Extract events (dates)
        events = rdap_data.get('events', [])
        for event in events:
            event_action = event.get('eventAction', '').lower()
            event_date = self._parse_rdap_date(event.get('eventDate'))
            
            if event_action == 'registration':
                creation_date = event_date
            elif event_action == 'expiration':
                expiration_date = event_date
            elif event_action == 'last changed' or event_action == 'last update':
                updated_date = event_date
        
        # Extract status
        status_list = rdap_data.get('status', [])
        for status_item in status_list:
            if isinstance(status_item, str):
                status.append(status_item)
            elif isinstance(status_item, dict):
                status.append(status_item.get('description', str(status_item)))
        
        # Extract name servers
        nameservers = rdap_data.get('nameservers', [])
        for ns in nameservers:
            if isinstance(ns, dict):
                ldh_name = ns.get('ldhName')
                if ldh_name:
                    name_servers.append(ldh_name.lower())
            elif isinstance(ns, str):
                name_servers.append(ns.lower())
        
        # Extract registrar
        entities = rdap_data.get('entities', [])
        for entity in entities:
            roles = entity.get('roles', [])
            if 'registrar' in roles:
                registrar = entity.get('vcardArray', [None, None, [['fn', {}, 'text', entity.get('name', '')]]])
                break
        
        # Extract contact information
        for entity in entities:
            roles = entity.get('roles', [])
            vcard = entity.get('vcardArray', [])
            
            if 'registrant' in roles:
                registrant = self._parse_vcard(vcard)
            elif 'administrative' in roles:
                admin_contact = self._parse_vcard(vcard)
            elif 'technical' in roles:
                tech_contact = self._parse_vcard(vcard)
        
        return DomainInfo(
            domain=domain,
            registrar=registrant.get('name') if registrant else None,
            creation_date=creation_date,
            expiration_date=expiration_date,
            updated_date=updated_date,
            status=status,
            name_servers=name_servers,
            registrant=registrant,
            admin_contact=admin_contact,
            tech_contact=tech_contact,
            raw_data=json.dumps(rdap_data, indent=2),
            source="rdap"
        )
    
    def _parse_rdap_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse RDAP date string"""
        if not date_str:
            return None
        
        try:
            # RDAP dates are typically in ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return None
    
    def _parse_vcard(self, vcard: List) -> Optional[Dict[str, Any]]:
        """Parse vCard data from RDAP"""
        if not vcard or len(vcard) < 3:
            return None
        
        contact_info = {}
        
        for item in vcard[2]:
            if len(item) >= 4:
                prop_name = item[0]
                prop_value = item[3]
                
                if prop_name == 'fn':
                    contact_info['name'] = prop_value
                elif prop_name == 'org':
                    contact_info['organization'] = prop_value
                elif prop_name == 'email':
                    contact_info['email'] = prop_value
                elif prop_name == 'tel':
                    contact_info['phone'] = prop_value
                elif prop_name == 'adr':
                    contact_info['address'] = prop_value
        
        return contact_info if contact_info else None
