#!/usr/bin/env python3
"""
Test script to demonstrate full contact information display
"""
import asyncio
from domain_checker.models import DomainInfo, LookupResult
from domain_checker.cli import display_domain_info
from datetime import datetime

# Create mock domain info with full contact details
mock_domain = DomainInfo(
    domain="example-with-contacts.com",
    registrar="Example Registrar Inc.",
    creation_date=datetime(2020, 1, 15, 10, 30, 0),
    expiration_date=datetime(2026, 1, 15, 10, 30, 0),
    updated_date=datetime(2024, 6, 20, 14, 45, 0),
    status=["client transfer prohibited", "client delete prohibited"],
    name_servers=["ns1.example.com", "ns2.example.com"],
    registrant={
        "name": "John Doe",
        "organization": "Acme Corporation",
        "email": "john.doe@example.com",
        "phone": "+1-555-0100",
        "address": "123 Main St, Suite 500, San Francisco, CA 94105, USA"
    },
    admin_contact={
        "name": "Jane Smith",
        "organization": "Acme IT Department",
        "email": "jane.smith@example.com",
        "phone": "+1-555-0101"
    },
    tech_contact={
        "name": "Bob Johnson",
        "email": "bob.johnson@example.com",
        "phone": "+1-555-0102",
        "address": "456 Tech Lane, Building 2, Austin, TX 78701, USA"
    },
    source="rdap",
    raw_data=""
)

# Create a lookup result
result = LookupResult(
    domain="example-with-contacts.com",
    success=True,
    data=mock_domain,
    lookup_time=0.25,
    method="rdap"
)

# Display it
print("\n🔍 Example of FULL contact information display:\n")
display_domain_info(result)

print("\n" + "="*80)
print("NOTE: Most modern RDAP servers hide detailed contact information")
print("for privacy reasons (GDPR compliance). This is a demonstration")
print("of what the CLI looks like when full contact details ARE available.")
print("="*80 + "\n")

