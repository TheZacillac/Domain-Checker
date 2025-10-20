"""
Custom exceptions for domain checker
"""


class DomainCheckerError(Exception):
    """Base exception for domain checker"""
    pass


class DomainLookupError(DomainCheckerError):
    """Error during domain lookup"""
    
    def __init__(self, domain: str, method: str, message: str, original_error: Exception = None):
        self.domain = domain
        self.method = method
        self.original_error = original_error
        super().__init__(f"Failed to lookup {domain} using {method}: {message}")


class WhoisError(DomainLookupError):
    """Error during WHOIS lookup"""
    
    def __init__(self, domain: str, message: str, original_error: Exception = None):
        super().__init__(domain, "whois", message, original_error)


class RdapError(DomainLookupError):
    """Error during RDAP lookup"""
    
    def __init__(self, domain: str, message: str, original_error: Exception = None):
        super().__init__(domain, "rdap", message, original_error)


class DigError(DomainLookupError):
    """Error during DIG lookup"""
    
    def __init__(self, domain: str, message: str, original_error: Exception = None):
        super().__init__(domain, "dig", message, original_error)


class ConfigurationError(DomainCheckerError):
    """Error in configuration"""
    pass


class RateLimitError(DomainCheckerError):
    """Rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message)


class TimeoutError(DomainCheckerError):
    """Operation timed out"""
    
    def __init__(self, operation: str, timeout: float):
        super().__init__(f"{operation} timed out after {timeout} seconds")


class ValidationError(DomainCheckerError):
    """Input validation error"""
    
    def __init__(self, field: str, value: str, message: str):
        super().__init__(f"Validation error for {field} '{value}': {message}")


class FileError(DomainCheckerError):
    """File operation error"""
    
    def __init__(self, file_path: str, operation: str, message: str):
        super().__init__(f"File {operation} error for '{file_path}': {message}")


class NetworkError(DomainCheckerError):
    """Network operation error"""
    
    def __init__(self, url: str, message: str, original_error: Exception = None):
        self.url = url
        self.original_error = original_error
        super().__init__(f"Network error for {url}: {message}")


class CacheError(DomainCheckerError):
    """Cache operation error"""
    
    def __init__(self, operation: str, message: str):
        super().__init__(f"Cache {operation} error: {message}")


class MCPError(DomainCheckerError):
    """MCP server error"""
    
    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(f"MCP error: {message}")
