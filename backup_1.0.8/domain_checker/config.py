"""
Configuration management for domain checker
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DomainCheckerConfig(BaseModel):
    """Configuration for domain checker"""
    
    # Timeout settings
    timeout: int = Field(default=30, ge=1, le=300, description="Default timeout in seconds")
    
    # Concurrency settings
    max_concurrent: int = Field(default=10, ge=1, le=100, description="Maximum concurrent lookups")
    rate_limit: float = Field(default=1.0, ge=0.1, le=10.0, description="Rate limit in requests per second")
    
    # Method preferences
    default_method: str = Field(default="auto", description="Default lookup method")
    prefer_rdap: bool = Field(default=True, description="Prefer RDAP over WHOIS when available")
    
    # Output settings
    show_raw_data: bool = Field(default=False, description="Show raw data in output")
    max_raw_data_length: int = Field(default=1000, description="Maximum length of raw data to display")
    
    # Cache settings
    enable_cache: bool = Field(default=False, description="Enable caching of results")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    cache_size: int = Field(default=1000, description="Maximum cache size")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # RDAP settings
    rdap_servers: Dict[str, str] = Field(
        default_factory=lambda: {
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
        },
        description="RDAP servers for different TLDs"
    )
    
    # User agent for HTTP requests
    user_agent: str = Field(
        default="DomainChecker/1.0.0 (https://github.com/domain-checker)",
        description="User agent string for HTTP requests"
    )
    
    # Retry settings
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum number of retries")
    retry_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Delay between retries in seconds")
    
    @classmethod
    def load_from_file(cls, config_path: str) -> "DomainCheckerConfig":
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except FileNotFoundError:
            return cls()
        except Exception as e:
            raise ValueError(f"Error loading config from {config_path}: {e}")
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to file"""
        try:
            config_data = self.dict()
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            raise ValueError(f"Error saving config to {config_path}: {e}")
    
    @classmethod
    def load_from_env(cls) -> "DomainCheckerConfig":
        """Load configuration from environment variables"""
        config_data = {}
        
        # Map environment variables to config fields
        env_mapping = {
            'DOMAIN_CHECKER_TIMEOUT': 'timeout',
            'DOMAIN_CHECKER_MAX_CONCURRENT': 'max_concurrent',
            'DOMAIN_CHECKER_RATE_LIMIT': 'rate_limit',
            'DOMAIN_CHECKER_DEFAULT_METHOD': 'default_method',
            'DOMAIN_CHECKER_PREFER_RDAP': 'prefer_rdap',
            'DOMAIN_CHECKER_SHOW_RAW_DATA': 'show_raw_data',
            'DOMAIN_CHECKER_MAX_RAW_DATA_LENGTH': 'max_raw_data_length',
            'DOMAIN_CHECKER_ENABLE_CACHE': 'enable_cache',
            'DOMAIN_CHECKER_CACHE_TTL': 'cache_ttl',
            'DOMAIN_CHECKER_CACHE_SIZE': 'cache_size',
            'DOMAIN_CHECKER_LOG_LEVEL': 'log_level',
            'DOMAIN_CHECKER_LOG_FILE': 'log_file',
            'DOMAIN_CHECKER_USER_AGENT': 'user_agent',
            'DOMAIN_CHECKER_MAX_RETRIES': 'max_retries',
            'DOMAIN_CHECKER_RETRY_DELAY': 'retry_delay',
        }
        
        for env_var, config_field in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if config_field in ['timeout', 'max_concurrent', 'max_raw_data_length', 'cache_ttl', 'cache_size', 'max_retries']:
                    config_data[config_field] = int(value)
                elif config_field in ['rate_limit', 'retry_delay']:
                    config_data[config_field] = float(value)
                elif config_field in ['prefer_rdap', 'show_raw_data', 'enable_cache']:
                    config_data[config_field] = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    config_data[config_field] = value
        
        return cls(**config_data)
    
    @classmethod
    def get_default_config_path(cls) -> str:
        """Get default configuration file path"""
        config_dir = Path.home() / '.config' / 'domain-checker'
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / 'config.json')
    
    @classmethod
    def load_default(cls) -> "DomainCheckerConfig":
        """Load default configuration (file -> env -> defaults)"""
        # Try to load from file first
        config_path = cls.get_default_config_path()
        try:
            return cls.load_from_file(config_path)
        except:
            pass
        
        # Try to load from environment
        try:
            return cls.load_from_env()
        except:
            pass
        
        # Return default configuration
        return cls()


# Global configuration instance
config = DomainCheckerConfig.load_default()
