"""
Connection pool manager for optimized HTTP connections
"""

import aiohttp
from typing import Optional


class ConnectionPool:
    """Manages HTTP connection pools for optimal performance"""
    
    def __init__(self, 
                 limit: int = 100,
                 ttl_dns_cache: int = 300,
                 keepalive_timeout: int = 60,
                 force_close: bool = False):
        """
        Initialize connection pool
        
        Args:
            limit: Maximum number of simultaneous connections
            ttl_dns_cache: DNS cache TTL in seconds
            keepalive_timeout: Keep-alive timeout in seconds
            force_close: Force close connections after each request
        """
        self.limit = limit
        self.ttl_dns_cache = ttl_dns_cache
        self.keepalive_timeout = keepalive_timeout
        self.force_close = force_close
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create session"""
        if self._session is None or self._session.closed:
            await self.create_session()
        return self._session
    
    async def create_session(self) -> aiohttp.ClientSession:
        """Create new session with optimized connector"""
        if self._session and not self._session.closed:
            await self._session.close()
        
        # Create optimized TCP connector
        self._connector = aiohttp.TCPConnector(
            limit=self.limit,
            limit_per_host=30,  # Max connections per host
            ttl_dns_cache=self.ttl_dns_cache,
            use_dns_cache=True,
            enable_cleanup_closed=True,
            force_close=self.force_close,
            keepalive_timeout=self.keepalive_timeout
        )
        
        # Create session with connector
        timeout = aiohttp.ClientTimeout(
            total=60,
            connect=10,
            sock_read=30
        )
        
        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=timeout,
            headers={
                'User-Agent': 'DomainChecker/1.0.0 (https://github.com/domain-checker)',
                'Accept': 'application/json, application/rdap+json, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
        )
        
        return self._session
    
    async def close(self):
        """Close session and connector"""
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None
        self._connector = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        return await self.get_session()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Don't close on exit - keep connections alive
        pass
    
    def stats(self) -> dict:
        """Get connection pool statistics"""
        if not self._connector:
            return {"active": False}
        
        return {
            "active": True,
            "limit": self.limit,
            "ttl_dns_cache": self.ttl_dns_cache,
            "keepalive_timeout": self.keepalive_timeout,
            "force_close": self.force_close
        }


# Global connection pool instance
_global_pool: Optional[ConnectionPool] = None


def get_global_pool() -> ConnectionPool:
    """Get global connection pool instance"""
    global _global_pool
    if _global_pool is None:
        _global_pool = ConnectionPool()
    return _global_pool


async def close_global_pool():
    """Close global connection pool"""
    global _global_pool
    if _global_pool:
        await _global_pool.close()
        _global_pool = None
