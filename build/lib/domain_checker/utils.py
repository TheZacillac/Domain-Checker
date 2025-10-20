"""
Utility functions for domain checker
"""

import re
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from .exceptions import ValidationError


def validate_domain(domain: str) -> str:
    """
    Validate and normalize domain name
    
    Args:
        domain: Domain name to validate
        
    Returns:
        Normalized domain name
        
    Raises:
        ValidationError: If domain is invalid
    """
    if not domain:
        raise ValidationError("domain", domain, "Domain cannot be empty")
    
    # Remove protocol if present
    if domain.startswith(('http://', 'https://')):
        parsed = urlparse(domain)
        domain = parsed.netloc or parsed.path
    
    # Remove www. prefix
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Remove trailing slash
    domain = domain.rstrip('/')
    
    # Basic domain validation regex
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    
    if not domain_pattern.match(domain):
        raise ValidationError("domain", domain, "Invalid domain format")
    
    # Check length
    if len(domain) > 253:
        raise ValidationError("domain", domain, "Domain too long (max 253 characters)")
    
    # Check for valid TLD
    parts = domain.split('.')
    if len(parts) < 2:
        raise ValidationError("domain", domain, "Domain must have at least one subdomain and TLD")
    
    tld = parts[-1]
    if len(tld) < 2:
        raise ValidationError("domain", domain, "TLD must be at least 2 characters")
    
    return domain.lower()


def validate_domains(domains: List[str]) -> List[str]:
    """
    Validate and normalize list of domain names
    
    Args:
        domains: List of domain names to validate
        
    Returns:
        List of normalized domain names
        
    Raises:
        ValidationError: If any domain is invalid
    """
    if not domains:
        raise ValidationError("domains", str(domains), "Domain list cannot be empty")
    
    validated_domains = []
    for domain in domains:
        try:
            validated_domain = validate_domain(domain)
            validated_domains.append(validated_domain)
        except ValidationError as e:
            raise ValidationError("domains", domain, f"Invalid domain in list: {e}")
    
    return validated_domains


def extract_tld(domain: str) -> str:
    """
    Extract TLD from domain name
    
    Args:
        domain: Domain name
        
    Returns:
        TLD (top-level domain)
    """
    parts = domain.split('.')
    return parts[-1].lower() if parts else ''


def is_valid_ip(ip: str) -> bool:
    """
    Check if string is a valid IP address
    
    Args:
        ip: IP address string
        
    Returns:
        True if valid IP address
    """
    # IPv4 pattern
    ipv4_pattern = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    # IPv6 pattern (simplified)
    ipv6_pattern = re.compile(
        r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$'
    )
    
    return bool(ipv4_pattern.match(ip) or ipv6_pattern.match(ip))


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human readable string
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1m 30s")
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    
    minutes = int(seconds // 60)
    seconds = seconds % 60
    
    if minutes == 0:
        return f"{seconds:.1f}s"
    elif minutes < 60:
        return f"{minutes}m {seconds:.1f}s"
    else:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}h {minutes}m {seconds:.1f}s"


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger("domain_checker")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def sanitize_output(data: Any, max_length: int = 1000) -> str:
    """
    Sanitize output data for display
    
    Args:
        data: Data to sanitize
        max_length: Maximum length of output
        
    Returns:
        Sanitized string
    """
    if data is None:
        return "N/A"
    
    data_str = str(data)
    
    if len(data_str) > max_length:
        return data_str[:max_length] + "... (truncated)"
    
    return data_str


def parse_domain_list(text: str) -> List[str]:
    """
    Parse domain list from text (one per line, comma separated, or space separated)
    
    Args:
        text: Text containing domains
        
    Returns:
        List of domain names
    """
    domains = []
    
    # Split by newlines first
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Split by commas
        if ',' in line:
            parts = line.split(',')
            for part in parts:
                part = part.strip()
                if part:
                    domains.append(part)
        else:
            # Split by spaces
            parts = line.split()
            for part in parts:
                part = part.strip()
                if part:
                    domains.append(part)
    
    return domains


def create_summary_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create summary statistics from lookup results
    
    Args:
        results: List of lookup results
        
    Returns:
        Summary statistics
    """
    total = len(results)
    successful = sum(1 for r in results if r.get('success', False))
    failed = total - successful
    
    methods = {}
    for result in results:
        method = result.get('method', 'unknown')
        methods[method] = methods.get(method, 0) + 1
    
    total_time = sum(r.get('lookup_time', 0) for r in results)
    avg_time = total_time / total if total > 0 else 0
    
    return {
        'total': total,
        'successful': successful,
        'failed': failed,
        'success_rate': (successful / total * 100) if total > 0 else 0,
        'methods': methods,
        'total_time': total_time,
        'average_time': avg_time,
        'fastest': min((r.get('lookup_time', 0) for r in results), default=0),
        'slowest': max((r.get('lookup_time', 0) for r in results), default=0)
    }
