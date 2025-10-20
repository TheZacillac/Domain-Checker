"""
Domain Checker - Asynchronous domain lookup with WHOIS and RDAP support
"""

__version__ = "1.3.1"
__author__ = "Domain Checker"
__email__ = "domain@example.com"

from .core import DomainChecker
from .models import DomainInfo, LookupResult
from .whois_client import WhoisClient
from .rdap_client import RdapClient
from .dig_client import DigClient
from .propagation_checker import DNSPropagationChecker, PropagationResult, PropagationSummary
from .updater import DomainCheckerUpdater
from .update_checker import UpdateChecker, quick_check

__all__ = [
    "DomainChecker",
    "DomainInfo",
    "LookupResult",
    "WhoisClient",
    "RdapClient",
    "DigClient",
    "DNSPropagationChecker",
    "PropagationResult",
    "PropagationSummary",
    "DomainCheckerUpdater",
    "UpdateChecker",
    "quick_check",
]
