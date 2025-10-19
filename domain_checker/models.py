"""
Data models for domain information
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DomainInfo(BaseModel):
    """Domain information from WHOIS or RDAP"""
    
    domain: str
    registrar: Optional[str] = None
    creation_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    status: List[str] = Field(default_factory=list)
    name_servers: List[str] = Field(default_factory=list)
    registrant: Optional[Dict[str, Any]] = None
    admin_contact: Optional[Dict[str, Any]] = None
    tech_contact: Optional[Dict[str, Any]] = None
    raw_data: Optional[str] = None
    source: str  # "whois" or "rdap"


class LookupResult(BaseModel):
    """Result of a domain lookup operation"""
    
    domain: str
    success: bool
    data: Optional[DomainInfo] = None
    error: Optional[str] = None
    lookup_time: float
    method: str  # "whois" or "rdap"


class BulkLookupResult(BaseModel):
    """Result of bulk domain lookup"""
    
    total_domains: int
    successful_lookups: int
    failed_lookups: int
    results: List[LookupResult]
    total_time: float
    average_time_per_domain: float
